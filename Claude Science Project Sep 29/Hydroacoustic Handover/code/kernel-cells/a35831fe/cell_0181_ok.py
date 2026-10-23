import json
vm={fn:aid for fn,aid in done}; json.dump(vm,open('withdrawn/vm.json','w')); print(json.dumps(vm))