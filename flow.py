"""Deterministic CSV reconciliation. No account, network, or paid API required."""
import argparse,csv,json,hashlib,sqlite3,os,tempfile
from decimal import Decimal,InvalidOperation
from pathlib import Path
def money(value):
    d=Decimal(str(value))
    if not d.is_finite() or d<0 or d.as_tuple().exponent < -2:raise ValueError('Amount must be non-negative with at most 2 decimal places')
    return int(d*100)
def process(source,output,state):
    raw=Path(source).read_bytes()
    if len(raw)>5_000_000:raise ValueError('CSV exceeds 5 MB limit')
    digest=hashlib.sha256(raw).hexdigest()
    con=sqlite3.connect(state)
    try:
        con.execute('CREATE TABLE IF NOT EXISTS runs(hash TEXT PRIMARY KEY, report TEXT NOT NULL)')
        prior=con.execute('SELECT report FROM runs WHERE hash=?',(digest,)).fetchone()
        if prior:report=json.loads(prior[0]);report['cached']=True
        else:
            import io
            reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),strict=True)
            if reader.fieldnames!=['invoice_id','customer','amount','paid']:raise ValueError('Expected invoice_id,customer,amount,paid header')
            rows=list(reader)
            accepted=[];rejected=[];seen=set()
            for line,row in enumerate(rows,2):
                try:
                    if None in row or any(v is None for v in row.values()):raise ValueError('Expected four columns')
                    key=row.get('invoice_id','').strip();customer=row.get('customer','').strip()
                    if not key or not customer:raise ValueError('Missing invoice_id or customer')
                    if key in seen:raise ValueError('Duplicate invoice_id in this file')
                    amount=money(row.get('amount',''));paid=money(row.get('paid',''))
                    if paid>amount:raise ValueError('Paid exceeds invoice amount')
                    seen.add(key)
                    accepted.append({'invoice_id':key,'customer':customer,'amount_cents':amount,'paid_cents':paid,'due_cents':amount-paid})
                except (ValueError,InvalidOperation) as e:rejected.append({'line':line,'error':str(e)})
            due=sum(x['due_cents'] for x in accepted)
            report={'sha256':digest,'cached':False,'accepted':accepted,'rejected':rejected,'totals':{'invoices':len(accepted),'due_cents':due},'summary':f'{len(accepted)} valid invoices; {len(rejected)} rejected rows; outstanding USD {due/100:.2f}.','summary_mode':'deterministic'}
            con.execute('INSERT OR IGNORE INTO runs VALUES(?,?)',(digest,json.dumps(report)));con.commit()
        target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
        fd,name=tempfile.mkstemp(dir=target.parent,suffix='.tmp')
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
            os.replace(name,target)
        finally:
            if os.path.exists(name):os.unlink(name)
        return report
    finally:con.close()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('--output',default='report.json');p.add_argument('--state',default='runs.db');a=p.parse_args()
    try:print(json.dumps(process(a.source,a.output,a.state)['totals']))
    except (OSError,ValueError,UnicodeError,csv.Error) as e:p.exit(1,f'Processing failed: {e}\n')
