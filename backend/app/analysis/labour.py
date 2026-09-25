import polars as pl

def labour_frames(frames,emit):
    df=frames['lfs_state_sex'].filter(pl.col('sex')=='both')
    result=[emit(df,column,metric,'lfs_state_sex') for column,metric in [('u_rate','unemployment'),('p_rate','labour_force_participation'),('lf_employed','employment')]]
    result.append(emit(frames['dosm_publication_18690'],'labour_productivity','labour_productivity','dosm_publication_18690'))
    population=frames['population_state'].filter((pl.col('sex')=='both')&(pl.col('age')=='overall')&(pl.col('ethnicity')=='overall'))
    result.append(emit(population,'population','population','population_state'))
    return result
