import boonnano as bn

success, nano=bn.open_nano('example','v3')
print(nano)
bn.configure_nano(nano,numeric_format='float',feature_count=20,min=-10,max=15,percent_variation=0.05)
success,config = bn.get_config(nano)
print(config)
bn.close_nano(nano)
