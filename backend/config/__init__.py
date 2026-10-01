# Use mysqlclient if it is installed, otherwise fall back to the pure-Python PyMySQL driver.
try:
    import MySQLdb  # noqa: F401
except ImportError:
    try:
        import pymysql

        pymysql.version_info = (2, 2, 1, "final", 0)  # satisfy Django's driver version check
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
