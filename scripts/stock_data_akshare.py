#!/usr/bin/env python3
"""
A股数据获取脚本 - 基于 AkShare 库
用于公众号数据简报的原始数据获取
"""
import akshare as ak
import pandas as pd


def get_financial_reports(code: str):
    """使用新浪财经接口获取三大报表（利润表、资产负债表、现金流量表）"""
    stock_prefix = f"sh{code}" if code.startswith('6') else f"sz{code}"
    income_stmt = ak.stock_financial_report_sina(stock=stock_prefix, symbol="利润表")
    balance_sheet = ak.stock_financial_report_sina(stock=stock_prefix, symbol="资产负债表")
    cashflow_stmt = ak.stock_financial_report_sina(stock=stock_prefix, symbol="现金流量表")
    return income_stmt, balance_sheet, cashflow_stmt


def extract_key_financials(income_stmt):
    """从利润表中提取关键财务指标"""
    latest_col = income_stmt.columns[0]
    revenue = income_stmt.loc['营业总收入', latest_col]
    net_profit = income_stmt.loc['归属于母公司所有者的净利润', latest_col]
    core_profit = income_stmt.loc['扣除非经常性损益后的净利润', latest_col]
    return {"revenue": revenue, "net_profit": net_profit, "core_profit": core_profit}


def get_cashflow_ocf(cashflow_stmt):
    """从现金流量表中提取经营性现金流净额"""
    latest_col = cashflow_stmt.columns[0]
    ocf = cashflow_stmt.loc['经营活动产生的现金流量净额', latest_col]
    return ocf


def get_valuation_data(code: str):
    """获取估值数据"""
    try:
        return ak.stock_value_em(symbol=code)
    except:
        try:
            return ak.stock_individual_info_em(symbol=code)
        except:
            return None


def get_insider_trading(code: str):
    """获取董监高增减持数据"""
    try:
        return ak.stock_gdfx_holding_change_em(symbol=code)
    except:
        return None


def get_shareholder_pledge(code: str):
    """获取股权质押数据"""
    try:
        return ak.stock_zy_em(symbol=code)
    except:
        return None


def get_company_announcements(code: str, page: int = 1):
    """获取公司公告列表"""
    try:
        return ak.stock_notice_report(symbol=code, page=page)
    except:
        return None


def check_inquiry_letter(announcements_df) -> bool:
    """检查是否有问询函"""
    if announcements_df is None:
        return False
    keywords = ['问询函', '问询', '关注函']
    titles = announcements_df['公告标题'].astype(str)
    return titles.str.contains('|'.join(keywords)).any()


def get_all_stock_data(code: str):
    """给定6位数字代码，返回所有需要的分析数据"""
    income_stmt, balance_sheet, cashflow_stmt = get_financial_reports(code)
    key_fin = extract_key_financials(income_stmt)
    ocf = get_cashflow_ocf(cashflow_stmt)
    valuation = get_valuation_data(code)
    insider = get_insider_trading(code)
    pledge = get_shareholder_pledge(code)
    announcements = get_company_announcements(code)
    has_inquiry = check_inquiry_letter(announcements)

    return {
        "company_code": code,
        "financials": key_fin,
        "operating_cashflow": ocf,
        "valuation": valuation,
        "insider_trading": insider,
        "shareholder_pledge": pledge,
        "has_inquiry_letter": has_inquiry,
        "announcements": announcements
    }


if __name__ == "__main__":
    # 示例：贵州茅台
    result = get_all_stock_data("600519")
    print(f"营收：{result['financials']['revenue']/1e8:.2f} 亿元")
    print(f"归母净利润：{result['financials']['net_profit']/1e8:.2f} 亿元")
