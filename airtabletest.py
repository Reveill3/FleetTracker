from airtable import Airtable

equipment = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Equipment', api_key='keyVE2OTPcmyTURGm')

print(equipment.search('UnitNumber', '53Q-11105'))
