import polars as pl

def gdp_frames(frames,emit):
    base=frames['gdp_state_real_supply'].filter((pl.col('series')=='abs')&(pl.col('sector')=='p0'))
    real=emit(base,'value','real_gdp','gdp_state_real_supply')
    prior=base.select('state',(pl.col('year')+1).alias('year'),pl.col('value').alias('previous_value'))
    growth=base.join(prior,on=['state','year'],how='inner').filter(pl.col('previous_value')>0).with_columns(((pl.col('value')/pl.col('previous_value')-1)*100).alias('growth'))
    return [real,emit(growth,'growth','gdp_growth','gdp_state_real_supply'),emit(frames['dosm_publication_19977'],'gdp_per_capita','gdp_per_capita','dosm_publication_19977')]
