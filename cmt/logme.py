# from http://devlishgenius.blogspot.com/2008/10/logging-in-real-time-in-python.html

import sys, os, os.path as op
import logging, subprocess

def getLog(fpath):
    logFormat = "%(levelname)-8s : %(asctime)s : %(name)-10s : %(message)s"
    logFormatter = logging.Formatter( logFormat )
    
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel( logging.DEBUG )
    consolehandler.setFormatter( logFormatter )
    
    if not op.exists(fpath):
        try:
            os.makedirs(op.dirname(fpath))
        except:
            pass
    
    logFile = fpath
    
    filehandler = logging.FileHandler( logFile )
    filehandler.setLevel( logging.DEBUG )
    filehandler.setFormatter( logFormatter )
    
    logging.getLogger( '' ).addHandler( consolehandler )
    logging.getLogger( '' ).addHandler( filehandler )
    
    mainlog = logging.getLogger( "main" )
    mainlog.setLevel( logging.DEBUG )
    
    return mainlog

def mkLocalLog( f ):
  # Could set _localLog as an attribute on the function:
  #   f._localLog = ..., but user would have to access it
  #  as an attribute: &lt;func&gt;._localLog( "&lt;msg&gt;" ).
  # Instead we add it to the function's globals dict.
  # If someone knows how to add it to the function's locals
  #  that would be great!

  ll = logging.getLogger( f.__name__ )
  ll.setLevel( logging.DEBUG )

  f.__globals__[ "_localLog" ] = ll
  return f

#@mkLocalLog
#def foo():
#  _localLog.info( "test" )
#
#foo()

@mkLocalLog
def runCmd( cmd, log ):

  try:
      os.unlink( "out_fifo" )
  except: pass

  os.mkfifo( "out_fifo" )

  try:
    
      fifo = os.fdopen( os.open( "out_fifo",
                                 os.O_RDONLY | os.O_NONBLOCK ) )

      newcmd = "( %s ) 1>out_fifo 2>&1"%( cmd, )

      process = subprocess.Popen( newcmd, shell = True,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.STDOUT )
      
      _localLog.debug( "Running: %s"%( cmd, ) )

      while process.returncode == None:
          # None means process is still running

          # need to poll the process once so the returncode
          # gets set (see docs)
          process.poll()

          try:
              line = fifo.readline().strip()
          except:
              continue

          if line:
              log.info( line )

      remaining = fifo.read()

      if remaining:
          for line in [ line
                        for line in remaining.split( "\n" )
                        if line.strip() ]:
              log.info( line.strip() )

      if process.returncode:
          _localLog.critical( "Return Value: %s"%( process.returncode, ) )
      else:
          _localLog.debug( "Return Value: %s"%( process.returncode, ) )

  finally:

      os.unlink( "out_fifo" )

def send_email_notification(message, to, log, host = 'localhost'):
    
    import smtplib
    
    sender = 'info@connectomics.org'
    receivers = to
    
    message = """From: Connectome Mapping Toolkit
To: %s
Subject: CMT - Notification

%s""" % (','.join(to), message)
    
    try:
        smtpObj = smtplib.SMTP(host)
        smtpObj.sendmail(sender, receivers, message)         
        log.info("Successfully sent email")    
    except smtplib.SMTPException:
        log.info("Error: Unable to send email")


