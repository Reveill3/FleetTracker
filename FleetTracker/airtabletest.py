from airtable import Airtable

movement = Airtable(base_key='appUv95IdpXpBkJ96',table_name='Movement', api_key='keyVE2OTPcmyTURGm')

print(movement.get_all()[0]['fields']['inTransit'])
