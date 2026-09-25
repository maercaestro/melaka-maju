from dataclasses import dataclass, asdict
@dataclass(frozen=True)
class Definition:
    label: str
    unit: str
    group: str
    dataset: str
    direction: str = 'descending'
    calculation: str | None = None

DEFINITIONS={
 'real_gdp':Definition('Real GDP','RM million','Economy','gdp_state_real_supply'),
 'gdp_growth':Definition('Real GDP growth','%','Economy','gdp_state_real_supply',calculation='(Real GDP / previous calendar year real GDP − 1) × 100'),
 'gdp_per_capita':Definition('GDP per capita','RM/person','Economy','dosm_publication_19977'),
 'manufacturing_share':Definition('Manufacturing share','%','Economy','gdp_state_real_supply',calculation='Manufacturing real GDP / total real GDP × 100'),
 'services_share':Definition('Services share','%','Economy','gdp_state_real_supply',calculation='Services real GDP / total real GDP × 100'),
 'agriculture_share':Definition('Agriculture share','%','Economy','gdp_state_real_supply',calculation='Agriculture real GDP / total real GDP × 100'),
 'construction_share':Definition('Construction share','%','Economy','gdp_state_real_supply',calculation='Construction real GDP / total real GDP × 100'),
 'median_household_income':Definition('Median household income','RM/month','Households','hies_state'),
 'mean_household_income':Definition('Mean household income','RM/month','Households','hies_state'),
 'mean_household_expenditure':Definition('Mean household expenditure','RM/month','Households','hies_state'),
 'gini':Definition('Gini coefficient','coefficient','Households','hies_state','ascending'),
 'poverty':Definition('Poverty rate','%','Households','hies_state','ascending'),
 'unemployment':Definition('Unemployment rate','%','Labour','lfs_state_sex','ascending'),
 'labour_force_participation':Definition('Labour-force participation','%','Labour','lfs_state_sex'),
 'employment':Definition('Employment',"thousand people",'Labour','lfs_state_sex'),
 'labour_productivity':Definition('Labour productivity','RM/worker','Economy','dosm_publication_18690'),
 'population':Definition('Population','thousand people','Population','population_state'),
}
def definitions(): return [{'id':key,**asdict(value)} for key,value in DEFINITIONS.items()]
