import sys
import hlib.env
import hlib.database
import hruntime

hlib.env.init_env(sys.argv[1])

print 'root'
hlib.database.dump(hruntime.dbroot['root'])
