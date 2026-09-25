import polars as pl
# Official gdp_lookup production codes, verified against DOSM's lookup table.
SECTORS={'manufacturing_share':'p3','services_share':'p5','agriculture_share':'p1','construction_share':'p4'}
def sector_frames(frames,emit):
    df=frames['gdp_state_real_supply'].filter(pl.col('series')=='abs')
    total=df.filter(pl.col('sector')=='p0').select('state','year',pl.col('value').alias('total'))
    result=[]
    for metric,sector in SECTORS.items():
        d=df.filter(pl.col('sector')==sector).join(total,on=['state','year'],how='inner').filter(pl.col('total')>0).with_columns((pl.col('value')/pl.col('total')*100).alias('share'))
        result.append(emit(d,'share',metric,'gdp_state_real_supply'))
    return result
