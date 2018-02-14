""" Prod3 MC Pipe Script to create a Transformation
          JB, LA April 2017
"""

from DIRAC.Core.Base import Script
Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s transName array_layout site particle pointing_dir zenith_angle nShower' % Script.scriptName,
                                     'Arguments:',
                                     '  transName: mcsim',                                     
                                     '  array_layout: demo',
                                     '  site: Paranal or LaPalma',
                                     '  particle: gamma, proton, electron',
                                     '  pointing_dir: North or South',
                                     '  zenith_agle: 20',
                                     '  nShower: from 5 to 25000',
                                     '\ne.g: %s Baseline Paranal gamma South 20 5'% Script.scriptName,
                                     ] ) )

Script.parseCommandLine()

import DIRAC
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient   
from DIRAC.Core.Workflow.Parameter import Parameter
from CTADIRAC.Interfaces.API.Prod3MCPipeBaselineTS2Job import Prod3MCPipeBaselineTS2Job
from DIRAC.DataManagementSystem.Client.MetaQuery import MetaQuery

def submitTS( transName, job, outputquery ):
  """ Create a transformation executing the job workflow  """

  ### Temporary fix to initialize JOB_ID #######
  job.workflow.addParameter( Parameter( "JOB_ID", "000000", "string", "", "", True, False, "Temporary fix" ) )
  job.workflow.addParameter( Parameter( "PRODUCTION_ID", "000000", "string", "", "", True, False, "Temporary fix" ) )
  job.setType('MCSimulation') ## Used for the JobType plugin

  transClient = TransformationClient()
  res = transClient.addTransformation( transName, 'MC Prod3 BaseLine test', 'corsika-simtel production', 'MCSimulation', 'Standard',
                                              'Manual', '', body=job.workflow.toXML(), outputMetaQuery=outputquery )

 
  if not res['OK']:
    print(res['Message'])
    DIRAC.exit( -1 )

#  t.setStatus( "Active" )
#  t.setAgentType( "Automatic" )
  
  return res

#########################################################

def runProd3( args = None ):
  """ Simple wrapper to create a Prod3MCPipeBaselineJob and setup parameters
      from positional arguments given on the command line.
      
      Parameters:
      args -- a list of 6 strings corresponding to job arguments
              array_layout site particle pointing_dir zenith_angle nShower
              demo LaPalma  gamma South 20 1000
  """
  # get arguments
  transName = args[0]
  layout = args[1]
  site = args[2]
  particle = args[3]
  pointing = args[4]
  zenith = args[5]
  nShower= args[6]

    ### Main Script ###
  job = Prod3MCPipeBaselineTS2Job()

  # override for testing
  job.setName('BL_LaPalma_20deg_%s'%particle)
  
  # package and version
  job.setPackage('corsika_simhessarray')
  job.setVersion( '2017-04-19' )  # final with fix for gamma-diffuse

  # layout, site, particle, pointing direction, zenith angle
  # demo, LaPalma,  gamma, South,  20
  job.setArrayLayout(layout)
  job.setSite(site)
  job.setParticle(particle)
  job.setPointingDir(pointing)
  job.setZenithAngle( zenith )
  ####
  job.setOutputDataLevel( 0 ) 
  job.setConfigurationId( 0 )  
  # 5 is enough for testing
  job.setNShower(nShower)

  ### Set the startrunNb here (it will be added to the Task_ID)
  startrunNb = '0'
  job.setStartRunNumber( startrunNb )

  # set run number for TS submission: JOB_ID variable left for dynamic resolution during the Job. It corresponds to the Task_ID
  job.setRunNumber( '@{JOB_ID}' )

  # get dirac log files
  job.setOutputSandbox( ['*Log.txt'] )

  # add the sequence of executables
  job.setupWorkflow(debug=False)

  # set the OutputMetaQuery
  outputquery = MetaQuery( job.outputquery ).getMetaQueryAsJson()

  # submit to the Transformation System
  res = submitTS( transName, job, outputquery )
    
  # debug
  Script.gLogger.info( job.workflow )

  return res

#########################################################
if __name__ == '__main__':

  args = Script.getPositionalArgs()
  if ( len( args ) != 7 ):
    Script.showHelp()
  try:
    res = runProd3( args )
    if not res['OK']:
      DIRAC.gLogger.error ( res['Message'] )
      DIRAC.exit( -1 )
    else:
      DIRAC.gLogger.notice( 'Done' )
  except Exception:
    DIRAC.gLogger.exception()
    DIRAC.exit( -1 )
