import boonnano as bn

bn.setup_connection('v2')
success, nano=bn.create_instance()
success, config = bn.generate_config('float',feature_count=20,min=-10,max=15,percent_variation=0.05)
bn.set_config(nano, config)
success,config = bn.get_config(nano)
print(config)
bn.close_connection()
