import polars as pl

def changes(current, previous, unit):
    if current is None or previous is None: return None
    absolute=current-previous
    return {'absolute':round(absolute,8),'percent':round((current/previous-1)*100,8) if previous and unit not in ('%','coefficient') else None,'unit':'percentage points' if unit=='%' else unit}

def household_frames(frames, emit):
    result=[]
    for field,metric in [('income_median','median_household_income'),('income_mean','mean_household_income'),('expenditure_mean','mean_household_expenditure'),('gini','gini'),('poverty','poverty')]:
        primary=emit(frames['hies_state'],field,metric,'hies_state')
        historical='hh_inequality_state' if field=='gini' else 'hh_income_state' if field.startswith('income_') else None
        if historical:
            history=frames[historical]
            if historical=='hh_income_state': history=history.filter(pl.col('year')!=2020)
            extra=emit(history,field,metric,historical).join(primary.select('state','year'),on=['state','year'],how='anti')
            primary=pl.concat([primary,extra])
        result.append(primary)
    return result
