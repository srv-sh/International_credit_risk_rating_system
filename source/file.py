
class graphPage:
    criteria = ['Leverage', '1. Financial Debt to Tangible Net Worth (DTN)', '2. Financial Debt to Total Assets (DTA)',
            'Liquidity', '1. Current Ratio (CR)', '2. Cash Ratio (Cash)',
            'Profitability', '1. Net Profit Margin (NPM)', '2. Return on Assets (ROA)', '3. Operating Profit to Operating Assets (OPOA)',
            'Coverage', '1. Interest Coverage (IC)', '2. Debt Service Coverage Ratio (DSCR)', '3. Operating Cashflow to Debt Ratio (CDR)', '4. Cashflow Coverage Ratio (CCR)',
            'Operational Efficiency', '1. Stock Turnover Days (STD)', '2. Trade Debtor Collection Days (TDCD)', '3. Asset Turnover (AT)',
            'Earning Quality', '1. Operating Cash Flow to Sales (CFS)', '2. Cashflow based accrual ratio (CAR)',
            'Total', 'Percentage']
    
    scales = [10, 7, 3, 10, 7, 3, 10, 5, 3, 2, 15, 3, 5, 4, 3, 10, 4, 3, 3, 5, 3, 2, 60, 100]

    Parameter = ['Total','Leverage','Liquidity','Profitability','Coverage','Operational Efficiency','Earning Quality']

    values = [60, 10, 10, 10, 15, 10, 5]

    color_rows = ['Leverage', 'Liquidity', 'Profitability', 'Coverage', 'Operational Efficiency', 'Earning Quality', 'Total', 'Percentage']

    remarks = ["", "Low preferable", "Low preferable", "", "High preferable", "High preferable", "", "High preferable", "High preferable", "High preferable", "", "High preferable", "High preferable", "High preferable", "High preferable", "", "Low preferable", "Low preferable", "High preferable","", "High preferable","Low preferable"]

#     label_color = ["Excellent", "Good", "Marginal", "Unacceptable"] 

    Parameter2 = ['Total', 'Performance Behavior', 'Business and Industry Risk',
              'Management Risk', 'Security Risk', 'Relationship Risk', 'Compliance Risk']
    
    criteria2= ['Performance Behavior', 'Performance behavior with lending banks', 'How many times the borrower was adversely classified in last 3 years', 'Aversely classified means the borrower\'s loans classified as per BB loan classifications policy i.e SS, DF, BL','','','','',
            'How many times the borrower\'s loans was rescheduled/ restructured in last 3 years', '','','','','',
            'Performance behavior with  suppliers/ Creditors', 'Did The Borrower Pay Its Suppliers/ Creditors Regularly In Last 1 Year', '',
            'Business and Industry Risk', 'Sales Growth', 'Sales growth means annual sales growth', 'The formula for calculating sales growth is [(current year sales - previous year sales)/ previous year sales]*100', '','','',
            'Age of Business', 'The number of years the borrower', 'engaged in this line of business', '','','',
            'Industry Prospects', 'Critical assessment of 5 (five) years prospect of industry and borrower\'s sales volatility', '* Volatility denotes sales volatility', '','',
            'Long-Term External Credit Rating of the Borrower', '', 'Rating Grade should be assigned in line with BB Rating Mapping as per BRPD', '', '',
            'Management Risk', 'Experience of the Management', 'Quality of the  management based on total number of years of experience of  the senior management in the Industry.', '* Senior Management means MD and next two tiers','','',
            'Existence of Succession Plan', '','','','','Auditing Firms', 'BSEC listed auditors are considered as recognized', '', '', 'Change In External Auditors In Last 4 Years', '','',
            'Security Risk', 'Primary Security','','','','','Collateral', '','','','', 'Eligible Collateral Coverage', 'The formula of eligible collateral coverage is [eligible collateral / total loans]','',
            '* Eligible collateral should be determined as per BRPD circular no 14 issued on September 23, 2012 (Para 07, Page 10).  (see annex: Eligible Collateral)', '','',
            'Type of Guarantee', '', 'Strong Corporate Guarantee means the credit rating of the guarantor should be at least 1 or 2 as per BB rating mapping mentioned in BRPD circular 18/2014 on Risk Based Capital Adequacy in line with Basel III.', '','','',
            'Relationship Risk', 'Account Conduct', '','','','',
            'Compliance Risk', 'Compliance with environmental rules, regulations and covenants', '','',
            'Corporate Governance', 'Independence of Management', '', 'Total', 'Percentage']
    
    

    param= ['','','',"0 time", "1 time", "2 times", "3 times", ">3 times", '', "0 time", "1 time", "2 times", "3 times", ">3 times",'', "Yes", "No",
        '','',">10%", "5% to 10%", "Less than 5%", '','','',">10 years", "7 to 10 years", "5 to 7 years", "4 to 5 years", "<4 years",'',
        "Growing and Low Volatility", "Stable", "Growing but High Volatility", "Declining", '', "1", "2&3", ">3", "Unrated",'','',
        "More than 10 years in the related line of business", "5 to 10 years in the related line of business", "Less than 5 years",'','',
        "Yes, with good capability of successor", "Yes, but questionable capacity of successor", "No successor", '', '',
        "Recognized Auditors", "Other Auditors", "Un audited", '', "Yes", "No",
        '','',"Fully Pledged Facilities", "Registered Hypothecation (1st Charge/1st Pari Passu Charge)/Assignment of Bill under Work Order", "2nd Charge/Inferior Charge", "No Security",
        '', "Registered Mortgage On Municipal Corporation/Prime Area Property", "Registered Mortgage On Pourashava/Semi-Urban/ Union Parishad Area Property", "Equitable Mortgage Or No Property But Plant And Machinery As Collateral", "No Collateral",
        '', ">100%", "80% to 100%", "70% to 80%", "50% to 70%", "<50%", '',
        "Government Guarantee and/or Bank Guarantee", "Strong Corporate Guarantee", "Personal Guarantees or Corporate Guarantee without Strong Financial Strength", "No support/guarantee",'',
        '',"More than 3 years Accounts having faultless record", "Less than 3 years Accounts having faultless record", "Accounts having satisfactory dealings with some late payments.", "Frequent past dues & irregular dealings in Account", '',
        '','',"Yes", "No", '',"Good Corporate Governance", "Questionable Corporate Governance", '','']
    
    score= [10, '','',5,4,3,1,0,'',4,3,2,1,0,'',1,0,7,'',2,1,0,'','','',2,1.5,1,0.5,0,'',1,0.75,0.5,0,'',2,1.5,0.5,0,7,'',2,1,0,0,'',2,1,0,'','',2,1,0,'',1,0,11,'',2,1.5,1,0,'',2,1.5,1,0,'',5,4,3,2,0,'',2,1.5,1,0,'',3,3,2,1,0,'',2,'',1,0,'',1,0,40,'']

