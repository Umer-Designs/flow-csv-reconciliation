from flow import process,money
import pytest,json
def test_decimal():assert money('0.29')==29
@pytest.mark.parametrize('value',['NaN','Infinity','-1','1.001','abc'])
def test_bad_money(value):
    with pytest.raises(Exception):money(value)
def test_pipeline(tmp_path):
    source=tmp_path/'a.csv';source.write_text('invoice_id,customer,amount,paid\nA,Demo,1.01,0.29\nA,Demo,1,0\nB,Demo,1,2\n')
    out=tmp_path/'report.json';state=tmp_path/'state.db'
    r=process(source,out,state);assert r['totals']=={'invoices':1,'due_cents':72};assert len(r['rejected'])==2
    assert process(source,out,state)['cached'] is True
    assert json.loads(out.read_text())['totals']['due_cents']==72
def test_empty(tmp_path):
    p=tmp_path/'empty.csv';p.write_text('invoice_id,customer,amount,paid\n')
    assert process(p,tmp_path/'r.json',tmp_path/'s.db')['totals']['invoices']==0
def test_bad_header(tmp_path):
    p=tmp_path/'bad.csv';p.write_text('wrong,headers\na,b\n')
    with pytest.raises(ValueError):process(p,tmp_path/'r.json',tmp_path/'s.db')
def test_quoted_name(tmp_path):
    p=tmp_path/'quoted.csv';p.write_text('invoice_id,customer,amount,paid\nA,"Studio, Demo",10.50,0\n')
    assert process(p,tmp_path/'r.json',tmp_path/'s.db')['accepted'][0]['customer']=='Studio, Demo'
