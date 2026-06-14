from .models import FinancialProduct

def seed_sample_products():
    samples = [
        {'product_code':'SAVING_BASIC_001','product_name':'소액 습관 적금','bank_name':'플렉스은행','product_type':FinancialProduct.SAVING,'base_rate':3.0,'max_rate':4.5,'save_term':12,'join_way':'모바일 가입','special_condition':'자동이체 우대'},
        {'product_code':'SAVING_SHORT_001','product_name':'6개월 목표 적금','bank_name':'로그은행','product_type':FinancialProduct.SAVING,'base_rate':2.8,'max_rate':4.2,'save_term':6,'join_way':'온라인 가입','special_condition':'카드 실적 우대'},
        {'product_code':'DEPOSIT_STABLE_001','product_name':'안정형 정기예금','bank_name':'세이브은행','product_type':FinancialProduct.DEPOSIT,'base_rate':3.2,'max_rate':3.7,'save_term':12,'join_way':'모바일 가입','special_condition':'조건 단순'},
    ]
    for data in samples:
        FinancialProduct.objects.update_or_create(product_code=data['product_code'], defaults=data)

def choose_products(monthly_analysis):
    seed_sample_products()
    summary = monthly_analysis.category_summary or {}
    top = max(summary.items(), key=lambda x: x[1])[0] if summary else None
    if monthly_analysis.total_amount >= 800000 or top in ['쇼핑','카페','문화생활']:
        return FinancialProduct.objects.filter(product_type=FinancialProduct.SAVING).order_by('-max_rate')[:3]
    return FinancialProduct.objects.all().order_by('-max_rate')[:3]
