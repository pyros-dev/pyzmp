Changelog
=========

0.0.14 (2016-08-10)
-------------------

- Removing release shell script. now done from setup.py. [alexv]

- Removing package.xml. doing thirdparty release from release repo now.
  [alexv]

- Moving docs to doc. [alexv]

- Merge branch 'docs' of https://github.com/asmodehn/pyzmp. [alexv]

  Conflicts:
    CHANGELOG.rst

- Added doc-requirements. [AlexV]

- Added tutorial and example changelog generated with gitchangelog.
  [AlexV]

- More docs about process managers... [AlexV]

- Added very basic rpc tutorial. [AlexV]

- First doc version generated with sphinx-apidoc. added CHANGELOG.
  [AlexV]

0.0.13 (2016-08-10)
-------------------

- Preparing 0.0.13. [alexv]

- Retrieving changes from indigo-devel, because it s building now and
  ready to be offloaded to release repo as patches. [alexv]

- Improved setup.py. now relying on twine for release. [alexv]

- Preparing version 0.0.12. [alexv]

0.0.12 (2016-08-09)
-------------------

- Preparing version 0.0.12. [alexv]

- Synchronizing package version for ROS. [alexv]

- Improving self test. [AlexV]

- Refining tox venvs to not use them for development. [AlexV]

- Reviewing tox and tests. [AlexV]

- Filling in README. [AlexV]

0.0.11 (2016-06-23)
-------------------

- Preparing version 0.0.11. [alexv]

- Listing pytest last in th dependency list to solve https://github.com
  /pytest-dev/pytest/issues/1652. [alexv]

0.0.10 (2016-06-23)
-------------------

- Preparing version 0.0.10. [alexv]

- Merge pull request #1 from asmodehn/deterministic_node_start. [AlexV]

  Deterministic node start

- Documenting test methods to make quantifiedcode happy. [alexv]

- Updated quantifiedcode badge to point to correct project. [alexv]

- Return exitcode 0 if update ran, but never returned one. made run()
  method overridable more or less like Process.run() fixed confusion
  between run&update arguments cosmetics. [alexv]

- Change on API for shutdown and run/target. now process a lazy delegate
  to allow easy restart. [AlexV]

- Small node improvements. WIP. [AlexV]

- Reviewing how we use zmp nodes and improving tests... WIP. [alexv]

- Making default behavior (call start() without args) bw compatible ( we
  don't know if node has started just yet) [alexv]

- Making default timeout infinite for start() and shutdown() just like
  multiprocessing.Process. [alexv]

- Waiting for node to be initialized before returning from start() call.
  made start() more determinist, tests more stricts, and added timeouts
  on start() and shutdown() [alexv]

- Removing site-packages since this is a pure python project. ROS test
  somewhere else. [alexv]

- Revert "travis with sudo to be able to install ros." [alexv]

  This reverts commit 7b59cdf84f4e83a8cb0f2c3242e64667d29323da.

- Revert "adding ROS install for travis tests" [alexv]

  This reverts commit 518fdadeca719e64140814b39a3c185b6da649d7.

- Travis with sudo to be able to install ros. [alexv]

- Calling py.test directly from tox. [alexv]

- Adding ROS install for travis tests. [alexv]

- Added files required by catkin-pip. [alexv]

- Now using pytest for testing. [alexv]

- Fixing release script tag command. [alexv]

0.0.9 (2016-05-04)
------------------

- Removed bloom from release script. tested with testpypi. [alexv]

- Small travis improvement. preparing v0.0.9. [alexv]

- Now using pytest and tox for testing. [alexv]

- Removing package.xml from manifest. [alexv]

- Adding basic travis first config. [alexv]

- Importing zmp from pyros, cleaning up pyros stuff. [alexv]

- Replacing obsolete navi/semantic_locations by new
  /rocon/semantics/locations. [alexv]

- Moved pyros and zmp sources, otherwise pyros was not find through egg
  link. [alexv]

- Added version. fixed tests in cmakelists. added default config file,
  removed useless testing config. added entry point for selftests. added
  requirements devel dependency to pyros-setup. [alexv]

- Cleaning up rosinterface __init__. now doing ros setup only in child
  node process, dynamically. parent process is isolated. [alexv]

- Cleaning up imports and fixing tests. [alexv]

- Refactored to add configuration at module, package and user levels.
  implified pyros-setup configuration from rosinterface. reviewed
  separation between node and interface to isolate all ros setup in
  child process. now doing ROS message conversion internally in
  rosinterface service and topic classes. fixed most tests. now uses six
  to improve python3 compatibility. [alexv]

- Starting to adapt to new configuration from pyros-setup. [alexv]

- Now using catkin_pure_python. [alexv]

- Merge pull request #71 from gitter-badger/gitter-badge. [AlexV]

  Add a Gitter chat badge to README.rst

- Add Gitter badge. [The Gitter Badger]

- Merge pull request #69 from asmodehn/multiclient. [AlexV]

  cosmetics, comments and small fixes...

- Cosmetics, comments and small fixes... [alexv]

- Merge pull request #62 from asmodehn/remove_unused_features. [AlexV]

  Remove unused features

- Readme regarding IoT. [alexv]

- Cosmetics. [alexv]

- Changing reinit method to a setup service. now reinitialize
  rosinterface everytime the list of services or topic passed by the
  user changes. refactor the base interface to hold local copy of system
  state. fix all tests. [alexv]

- Added missing rosservice dependency. [alexv]

- Fixing package dependencies for catkin. [alexv]

- Fixing catkin build. [alexv]

- Removing unused ROS service specifications. [alexv]

- Merge branch 'improve_exceptions_handling' into
  remove_unused_features. [alexv]

- Improved exception handling. adding mock client to make unittests
  easy. cosmetics. [alexv]

- Improved Readme. [AlexV]

- Removing dynamic_reconfigure. [alexv]

- Removed rocon feature. cleanup. [alexv]

- Exposing servicecall timeout exception. cosmetics. [alexv]

- Merge pull request #55 from stonier/verbosity. [AlexV]

  Logging : WARN -> INFO

- Warn -> info when it's not meant to be alarming to the users. [Daniel
  Stonier]

- Fixing log warn -> info for startup args. [alexv]

- Fixme comments. [alexv]

- Merge commit '971199c' into indigo-devel. [alexv]

- Adding simple test to assert rospy potentially strange behaviors.
  separating cache and non cache tests. catching connection_cache proxy
  init timeout, showing error and disabling. [alexv]

- Merge commit '15aab53' into indigo-devel. [alexv]

- Adding custom manager argument in basenode, and making shutdown
  possible override more obvious. [alexv]

- ZMP : services and node advertisement now done in context managers.
  Node now support using custom context manager when starting in another
  process. cosmetics. [alexv]

- Improving base support to pass diff instead of query full state
  everytime. now with callback called from connection cache proxy to
  only process list if change happens. [alexv]

- Merge pull request #48 from asmodehn/connection_cache. [Daniel
  Stonier]

  Connection cache

- Fixing reinit to be delayed if ros interface not ready yet. [alexv]

- Fixing pyrosROS test with latest pyros_test. [alexv]

- Adding pyrosRos test to catkin tests. [alexv]

- Reiniting connection cache if dynamic_reconfigure disable/enable it.
  [alexv]

- Merge branch 'strict-python-exp' into connection_cache. [alexv]

- Using enable_cache in dynamic_reconfigure to be able to dynamically
  switch if needed. [alexv]

- Fixed populating empty message instance. comments. [alexv]

- Merge pull request #50 from asmodehn/strict-python-exp. [AlexV]

  Strict python experiment

- Merge branch 'connection_cache' of https://github.com/asmodehn/pyros
  into strict-python-exp. [alexv]

- Adding missing rosnode as test dependency. [AlexV]

- Disabling roconinterface dynamic import. [AlexV]

- Moving more nodes to pyros-test. [AlexV]

- Moving nodes to pyros-test. skipping tests if connection_cache not
  found. [AlexV]

- Better error message if tests are run from python without pyros-test
  installed in ROS env. [AlexV]

- Using pyros_cfg and fix import in rocont interface, to run nosetests
  from python venv. [AlexV]

- Added generated code for dynamic_reconfigure. [AlexV]

- Adding requirements, fixing setup.py for setuptools. [AlexV]

- Merge pull request #49 from asmodehn/pyros_setup_fixes. [AlexV]

  now allowing to delay the import of rosinterface subpackage and passi…

- Now allowing to delay the import of rosinterface subpackage and
  passing base_path to find ROS environment dynamically. [alexv]

- Using ros-shadow-fixed for travis. [AlexV]

- Cleaning up comments. [alexv]

- Adding option to enable cache or not from rosparams. [alexv]

- Ros_interface now using topics and service types from cacche if
  available, otherwise query one by one when needed. making sure cache
  process is started and stopped during the test to avoid scary harmless
  warnings. [alexv]

- Improving tests. [alexv]

- Using silent fallback for connectioncache proxy. [alexv]

- Fixing dependencies in package.xml. [alexv]

- Pyros now dependein on pyros_setup and pyros_test for tests. [alexv]

- Pyros now depending on pyros_setup. [alexv]

- Expose_transients_regex now relying on _transient_change_detect
  directly. small refactor to allow transient updates only with ROS
  system state differences. fixing mockinterface to call reinit only
  after setting up mock Added first connection_cache subscriber
  implementation to avoid pinging the master too often. WIP. [alexv]

0.0.8 (2016-01-25)
------------------

- Doing zmp tests one by one to workaround nose hanging bug with option
  --with-xunit. [alexv]

- Merge pull request #45 from asmodehn/update_timed. [AlexV]

  ZMP node now passing timedelta to update.

- Making service and param new style classes. [alexv]

- Fixing throttling to reinitialize last_update in basenode. [alexv]

- Fixing a few quantifiedcode issues... [alexv]

- ZMP node now passing timedelta to update. Pyros nodes now have a
  throttled_update method to control when heavy computation will be
  executed ( potentially not every update) [alexv]

- Displaying name of ROS node in log when starting up. [alexv]

- Mentioning dropping actions support in changelog. [alexv]

- Overhauled documentation. [alexv]

- Cosmetics. [alexv]

- Exposing pyros service exceptions for import. [alexv]

- Adding node with mute publisher for tests. [alexv]

- Fixing basic test nodes return message type. cosmetics. [alexv]

- Reviewing README. [alexv]

- Changelog for 0.1.0. cosmetics. [alexv]

- Merge pull request #43 from asmodehn/autofix/wrapped2_to3_fix. [AlexV]

  Fix "Prefer `format()` over string interpolation operator" issue

- Migrated `%` string formating. [Cody]

- Fixing badges after rename. [alexv]

- Merge pull request #42 from asmodehn/autofix/wrapped2_to3_fix. [AlexV]

  Fix "Avoid mutable default arguments" issue

- Avoid mutable default arguments. [Cody]

- Merge pull request #41 from asmodehn/mp_exception. [AlexV]

  Multiprocess

- Made namedtuple fields optional like for protobuf protocol. [alexv]

- Fixing zmp tests with namedtuple protocol. [alexv]

- Fixing catkin cmakelists after test rename. [alexv]

- Making client exceptions also PyrosExceptions. [alexv]

- Begining of implementation of slowservice node for test. not included
  in tests yet. [alexv]

- Removed useless hack in travis cmds, fixed typo. [alexv]

- Trying quick hack to fix travis build. [alexv]

- Adding status message when creating linksto access catkin generated
  python modules. [alexv]

- Adding zmp tests to catkin cmakelists. [alexv]

- Added dummy file to fix catkin install. [alexv]

- Small install and deps fixes. [alexv]

- Simplifying traceback response code in node. [alexv]

- Fixing unusable traceback usecase in zmp. [alexv]

- Cosmetics. adding basemsg unused yet. [alexv]

- Moving exception to base package, as they should be usable by the
  client of this package. [alexv]

- Making pyros exceptions pickleable. minor fixes to ensure exception
  propagation. [alexv]

- Comments. [alexv]

- Ros_setup now use of install workspace optional. fixes problems
  running nodes ( which needs message types ) from nosetests. [alexv]

- Added cleanup methods for transients. it comes in handy sometime ( for
  ROS topics for example ). [alexv]

- Pretty print dynamic reconfigure request. [alexv]

- Cleanup debug logging. [alexv]

- Adding logic on name was not a good idea. breaks underlying systems
  relaying on node name like params for ROS. [alexv]

- Removing name from argv, catching keyboard interrupt from pyros ros
  node. cosmetics. [alexv]

- Increasing default timeouts for listing services call form pyros
  client. [alexv]

- Fixed multiprocess mutli pyros conflict issues with topics with well
  known rosparam. now enforcing first part of node name. cosmetics.
  [alexv]

- Removed useless logging. [alexv]

- Adding basetopic and fixed topic detection in rosinterface. zmp
  service now excepting on timeout. [alexv]

- Fixed exceptions handling and transfer. fixed serialization of
  services and topic classes for ROSinterface. [alexv]

- Now reraise when transient type resolving or transient instance
  building fails. added reinit methods to list of node service to be
  able to change configuration without restarting the node ( usecase :
  dynamic reconfigure ) added option to PyrosROS node to start without
  dynamic reconfigure (useful for tests and explicit reinit) added some
  PyrosROS tests to check dynamic exposing of topics. cleaned up old
  rostful definitions. cosmetics. [alexv]

- Cleaning up old action-related code. fixed mores tests. [alexv]

- Fixing how to get topics and services list. commented some useless
  services ( interactions, ationcs, etc. ). [alexv]

- Changing version number to 0.1.0. preparing for minor release. [alexv]

- Refactoring ros emulated setup. [alexv]

- Improving and fixing rosinterface tests. still too many failures with
  rostest. [alexv]

- Fixing tests for Pyros client, and fixed Pyros client discovery logic.
  cosmetics. [alexv]

- Making RosInterface a child of BaseInterface and getting all Topic and
  test services to pass. cosmetics. [alexv]

- Improved test structure for rostest and nose to collaborate... [alexv]

- WIP. reorganising tests, moved inside package, nose import makes it
  easy. still having problems with rostest. [alexv]

- Fixing testTopic for rostest and nose. cosmetics. [alexv]

- Finishing python package rename. [alexv]

- Separated rospy / py trick from test. [alexv]

- Fixing testRosInterface rostest to be runnable from python directly,
  and debuggable in IDE, by emulating ROS setup in testfile. [alexv]

- Implemented functional API, abstract base interface class,
  mockinterface tests. [alexv]

- Moving and fixing tests. [alexv]

- Merge branch 'indigo-devel' of https://github.com/asmodehn/pyros into
  mp_exception. [alexv]

  Conflicts:
    setup.py
    src/rostful_node/rostful_node_process.py

- Changing ros package name after repository rename. [alexv]

- Fixing setup.py for recent catkin. [alexv]

- Protecting rospy from unicode args list. [alexv]

- Implemented transferring exception information via protobuf msg.
  readding tblib as dependency required for trusty. [alexv]

- WIP. starting to change message to be able to just not send the
  traceback if tblib not found. [alexv]

- Restructuring code and fixing all tests to run with new zmp-based
  implementation. [alexv]

- Now able to use bound methods as services. [alexv]

- Adding python-tblib as catkin dependency. [alexv]

- Useful todo comments. [alexv]

- Now using pickle is enough for serialization. getting rid of extra
  dill and funcsig dependencies. [alexv]

- Not transmitting function signature anymore. not needed for python
  style function matching. [alexv]

- Added cloudpickle in possible serializer comments. [alexv]

- Now forwarding all exceptions in service call on node fixed all zmp
  tests. [alexv]

- Fixing all zmp tests since we changed request into args and kwargs.
  [alexv]

- Starting to use dill for serializing functions and params. [alexv]

- Adding comments with more serialization lib candidates... [alexv]

- WIP. looking for a way to enforce arguments type when calling a
  service, and parsing properly when returning an error upon exception.
  [alexv]

- Getting message to work for both protobuf and pickle. Now we need to
  choose between tblib and dill for exception serialization. [alexv]

- Adding dill as dependency. [alexv]

- Multiprocess simple framework as separate zmp package. [alexv]

- Comments. [alexv]

- Transferring exceptions between processes. [alexv]

- Fixing all service tests and deadlock gone. [alexv]

- Improved service and node tests. still deadlock sometimes... [alexv]

- Multiprocess service testing okay for discover. [alexv]

- WIP. starting to use zmq for messaging. simpler than other
  alternatives. [alexv]

- WIP implementing service. [alexv]

- WIP adding mockframework a multiprocess communication framework.
  [alexv]

- Adding mockparam. [alexv]

- Adding code health badge. [alexv]

- Adding requirements badge. [alexv]

- Adding code quality badge. [alexv]

- Adding echo tests for mocktopic and mockservice. [alexv]

- Renaming populate / extract commands. [alexv]

- Setting up custom message type and tests for mock interface. [alexv]

- Fixing mockmessage and test. [alexv]

- Improving mockmessage and tests. [alexv]

- Started to build a mock interface, using python types as messages.
  This should help more accurate testing with mock. [alexv]

- Adding six submodule. tblib might need it. otherwise it might come in
  useful anyway. [alexv]

- Adding tblib to be able to transfer exception between processes.
  [alexv]

- Fixing travis badge. [alexv]

- Adding travis badge. [alexv]

- Merge branch 'indigo-devel' of https://github.com/asmodehn/rostful-
  node into indigo-devel. [alexv]

- Merge pull request #33 from asmodehn/travis. [AlexV]

  starting travis integration for autotest

- Starting travis integration for autotest. [alexv]

- Adding rostopic as a test_depend. [alexv]

- Merge pull request #32 from asmodehn/params. [AlexV]

  Params

- Fixes to make this node work again with rostful cosmetics and
  cleanups. [alexv]

- First implementation to expose params to python the same way as we do
  for topics and services. [alexv]

0.0.7 (2015-10-12)
------------------

- 0.0.7. [alexv]

- Adding log to show rostful node process finishing. [alexv]

- Change message content check to accept empty dicts. [Michal
  Staniaszek]

- Fixing corner cases when passing None as message content. invalid and
  should not work. [alexv]

- Fixing tests. and changed api a little. [alexv]

- Merge branch 'indigo-devel' of https://github.com/asmodehn/rostful-
  node into subprocess. [alexv]

- Removing useless fancy checks to force disabling rocon when set to
  false. updated rapp_watcher not working anymore. [AlexV]

- Rocon_std_msgs changed from PlatformInfo.uri to MasterInfo.rocon_uri.
  [AlexV]

- Send empty dicts instead of none from client. [Michal Staniaszek]

- Merge branch 'subprocess' of https://github.com/asmodehn/rostful-node
  into subprocess. [alexv]

- Service and topic exceptions caught and messages displayed. [Michal
  Staniaszek]

- Fleshed out topic and service info tuples. [Michal Staniaszek]

- Can check for rocon interface, get interactions. [Michal Staniaszek]

- Listing functions for client, corresponding mock and node functions.
  [Michal Staniaszek]

- Now passing stop_event as an argument to the spinner. cosmetics.
  [alexv]

- Fix when running actual rostfulnode. [alexv]

- Now running rostful_node in an separate process to avoid problems
  because of rospy.init_node tricks. [alexv]

- Cosmetics. [alexv]

- Improving how to launch rostest test. fixed hanging nosetest. hooking
  up new test to catkin. [alexv]

- Force-delete for services, test for removal crash on expose. [Michal
  Staniaszek]

  Test service nodes added

- Fix crash when reconfigure removes topics, started on unit tests.
  [Michal Staniaszek]

- Fixing removing from dictionary topic_args. [alexv]

- Merge pull request #28 from asmodehn/multi-instance-delete. [AlexV]

  Fixed topic deletion when multiple publishers/subscribers exist on the same topic

- Stopped removal of slashes from front of topics. [Michal Staniaszek]

- Fixed regex and add/remove issues with topics and services. [Michal
  Staniaszek]

- Fixed topic deletion, multiple calls to add. [Michal Staniaszek]

  The interface now tracks how many calls have been made to the add function and
  ensures that topics are not prematurely deleted from the list. Actions also have
  a similar thing going on, but not sure if it works since they are unused.
  Services are unchanged.

  Ensured uniqueness of topics and services being passed into the system using sets.

  Removed unnecessary ws_name code.

  Issue #27.

- Merge pull request #26 from asmodehn/wildcards. [AlexV]

  full regex, fixed reconfigure crash

- Merge branch 'indigo-devel' into wildcards. [Michal Staniaszek]

  Conflicts:
    src/rostful_node/ros_interface.py

- Merge pull request #23 from asmodehn/waiting-fix. [AlexV]

  Services are no longer lost, waiting lists are used more logically.

- Fix *_waiting list usage, service loss no longer permanent. [Michal
  Staniaszek]

  The lists *_waiting now contain topics, services or actions which we are
  expecting, but do not currently exist. Once it comes into existence, we remove
  it from this list.

  When services disconnect, their loss is no longer permanent. This had to do with
  the services being removed and not added to the waiting list.

  Fixes issue #21.

- Full regex, fixed reconfigure crash. [Michal Staniaszek]

  Can now use full regex in topic or service strings to match incoming strings.

  Fixed crash when dynamic reconfigure receives an invalid string

- Merge pull request #22 from asmodehn/feature-devel. [AlexV]

  Wildcard implementation

- Strings with no match characters don't add unwanted topics. [Michal
  Staniaszek]

  Regex fixed with beginning and end of line expected, previously would allow a
  match anywhere in the string.

  Issue #17.

- Removed separate lists for match strings. [Michal Staniaszek]

- Remove printing, unnecessary adding to _args arrays. [Michal
  Staniaszek]

- Adding wildcard * for exposing topics or services. [Michal Staniaszek]

  Implementation should be such that other match characters can be easily added if
  necessary.

  Fixes issue #17.

- Added TODO. [alexv]

- Added exception catching for when rocon interface is not available.
  [Michal Staniaszek]

- Added important technical TODO. [alexv]

- Fixing bad merge. [alexv]

- Fixing unitests after merge. [AlexV]

- Merge branch 'indigo-devel' of https://github.com/asmodehn/rostful-
  node into rosless. [AlexV]

  Conflicts:
  	src/rostful_node/rostful_client.py
  	src/rostful_node/rostful_node.py

- Quick fix to keep disappeared topics around, waiting, in case they
  come back up... [alexv]

- Turning off consume/noloss behavior. should not be the default. should
  be in parameter another way to expose topics. [AlexV]

- Allowing to call a service without any request. same as empty request.
  [AlexV]

- Keeping topics alive even after they disappear, until all messages
  have been read... WIP. [AlexV]

- Preparing for release 0.0.6. setup also possible without catkin.
  [AlexV]

- Changing rostful node design to match mock design. [AlexV]

- Fixing RostfulCtx with new Mock design. added unittest file. [AlexV]

- Improved interface of rostful client. added unit tests for
  rostfulClient. [AlexV]

- Improved interface of rostful mock, now async_spin return the pipe
  connection. added more unit tests for rostful mock. [AlexV]

- Added rostful mock object ( useful if no ROS found ). improved
  structure and added small unit test. [AlexV]

- Merge branch 'indigo-devel' of https://github.com/asmodehn/rostful-
  node into indigo-devel. [AlexV]

- Changing cfg file name to fix install. [AlexV]

- Comments TODO to remember to fix hack. [AlexV]

- Tentative fix of cfg... comments. [AlexV]

- Adding python futures as dependency. [AlexV]

- Commenting out icon image. no cache home on robot. need to find a new
  strategy. [AlexV]

- Removed useless broken services. [AlexV]

- Merge pull request #16 from asmodehn/indigo. [AlexV]

  fixing catkin_make install with dynamic reconfigure.

- Fixing catkin_make install with dynamic reconfigure. [AlexV]

- Adding bloom release in release process to sync with pypi release.
  [AlexV]

- Fixes for release and cosmetics. [AlexV]

- Preparing pypi release. [AlexV]

- Merge branch 'indigo-devel' of https://github.com/asmodehn/rostful-
  node into indigo-devel. [AlexV]

- Improving rostful node API. Adding rostful pipe client and python pipe
  protocol. removed redundant ros services. [AlexV]

- Simplifying rapp start and stop by using rapp_watcher methods. [AlexV]

- Now starting and stopping rapp. still ugly. [AlexV]

- Fixes to get rocon features to work again. [AlexV]

0.0.3 (2015-07-01)
------------------

- Preparing pypi release. small fix. [AlexV]

- Adding helper services to access Rosful node from a different process.
  Hacky, working around a limitation of rospy ( cannot publish on a
  topic created in a different process for some reason...). Proper
  design would be to call directly the python method ( work with
  services - node_init not needed ) [AlexV]

- Small cleanup. [AlexV]

- Adding context manager for rospy.init_node and rospy.signal_shutdown.
  No ROS signal handlers anymore. Cleanup properly done when program
  interrupted. [AlexV]

- Playing with signal handlers... [AlexV]

- Improved test. but topic interface not symmetric. needs to deeply test
  message conversion. [AlexV]

- Small fixes and first working test to plug on existing topic. [AlexV]

- Adding first copy from rostful. splitting repo in 2. [AlexV]

- Initial commit. [AlexV]


