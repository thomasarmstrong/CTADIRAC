""" Prod3 MC Script to run simtel_array for a given configuration
"""

from DIRAC.Core.Base import Script
Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s corsika input file list' % Script.scriptName,
                                     'Arguments:',
                                     '  inputfiles: corsika input file list',
                                     '\ne.g: %s corsika.list' % Script.scriptName,
                                     ] ) )

Script.parseCommandLine()

import DIRAC
from CTADIRAC.Interfaces.API.Prod3MCUserJob import Prod3MCUserJob
from DIRAC.Interfaces.API.Dirac import Dirac

def submitWMS( job, infileList ):
  """ Submit the job locally or to the WMS  """
  
  job.setParameterSequence( 'InputData', infileList, addToWorkflow = 'ParametricInputData' )
  job.setOutputData( ['*simtel.gz'], outputPath='simtel_data' )
  job.setOutputSandbox( ['*Log.txt'] )
  job.setInputSandbox( ['mycfg'] )
  job.setName( 'simteljob' )
  # To allow jobs run at other sites than the site where the InputData are located
  #job.setType( 'DataReprocessing' )

  dirac = Dirac()
  res = dirac.submit( job )

  if res['OK']:
    Script.gLogger.info( 'Submission Result: ', res['Value'] )

  return res

def runProd3( args = None ):
  """ Simple wrapper to create a Prod3MCUserJob and setup parameters
      from positional arguments given on the command line.
      
      Parameters:
      args -- corsika input file list
  """

  # get arguments
  infile = args[0]
  f = open( infile, 'r' )

  infileList = []
  for line in f:
    infile = line.strip()
    if line != "\n":
      infileList.append( infile )

  ### Main script
  job = Prod3MCUserJob()

  # set package version: to be set before setupWorkflow
  job.setPackage('corsika_simhessarray')
  job.setVersion( '2017-09-01' )

  ## set sim_telarray config
  job.setSimtelCfg( 'CTA-ULTRA6-SST-ASTRI_PROTO.cfg' ) # This is just an example. This file must be taken from your config. tarball 
  job.setSimtelOpts('ALTITUDE=1740 ATMOSPHERIC_TRANSMISSION=atm_trans_1740_6_10_0_0_1740.dat MAXIMUM_TELESCOPES=1 TRIGGER_TELESCOPES=1 ONLY_TRIGGERED_TELESCOPES=1 TELESCOPE_PHI=180.0 TELESCOPE_THETA=20.0 OUTPUT_FORMAT=1 SAVE_PHOTONS=2') # This is just an example, if you want to pass extra options in the command line

  # ## setup workflow: set executable and parameters
  job.setupWorkflow()

  ## group input files and submit
  res = submitWMS( job, infileList )

  # debug
    #Script.gLogger.info( job.workflow )

  return res

#########################################################
if __name__ == '__main__':

  args = Script.getPositionalArgs()
  if ( len( args ) != 1 ):
    Script.showHelp()
  try:
    res = runProd3( args )
    if not res['OK']:
      DIRAC.gLogger.error ( res['Message'] )
      DIRAC.exit( -1 )
    else:
      DIRAC.gLogger.notice( res['Value'] )
  except Exception:
    DIRAC.gLogger.exception()
    DIRAC.exit( -1 )
