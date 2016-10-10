from salts_prj.ini import ini_manager

def run():
    try:
        ini_manager.sync()
    except Exception, exc:
        print "Exception: %s" % exc
