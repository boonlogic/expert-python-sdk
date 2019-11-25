import boonnano as bn

success, nano=bn.open_nano('example','v3')
print('\n',success,nano, '\n')
bn.configure_nano(nano,numeric_format='float',feature_count=20,min=-10,max=15,percent_variation=0.05)
success,config = bn.get_config(nano)
print(config, '\n')
success = bn.configure_nano(nano,config=config)
bn.close_nano(nano)