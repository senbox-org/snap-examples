⚠ **The Jython approach is not fully elaborated and therefore not well documented. If you would like to use 
Jython and need assistance, please show up in the SNAP Forum. We discourage the usage of Jython. As of SNAP 8 
the Jython support is not part of the SNAP standard distribution anymore. However, the documentation 
referring to the usage of Jython in earlier SNAP versions is kept below.**

**See issue: [SNAP-1326: Provide snap-jython as seperate plugin](https://senbox.atlassian.net/browse/SNAP-1326)**

### Configuration

The Jython approach doesn't need any explicit configuration as Jython is bundled with SNAP.

### Using the SNAP Java API from Jython

It is currently not possible to use the SNAP Java API from Jython scripts. This issue will be addressed.
️
### Extending SNAP

#### Jython plugin

SNAP can be extended using SNAP Jython plugins. A Jython plugin is basically a directory or ZIP file which 
contains one or more Python modules which define a plugin activator class. Plugin activators are enumerated 
in a plugin registration file:

* `<plugin-dir>`
  * `one_plugin.py`
  * `another_plugin.py`
  * `META-INF`
    * `services`
      * `org.esa.snap.jython.PluginActivator`

When any SNAP application starts, for example SNAP Desktop (`bin/snap`) or the graph processing tool (`bin/gpt`), 
it loads all plugins found in a number of configurable locations. The first location is the `.snap/snap-jython`
directory of the users home directory. Other locations can be configured using the configuration parameter
`snap.jythonExtraPaths` whose value is a colon- (Unix/Darwin) or semicolon- (Windows) separated list of 
directories to search for plugins.

#### Plugin activator class

A SNAP extension is a Python class (with any name) defined in a Jython module that defines a no-args start 
and stop method:

```
class PluginActivator:

    def start(self):
        """ 
        The start method is called once while the SNAP Desktop application is being started. 
        You would put code here for registrating UI-elements such as actions and windows here.
        """
        pass
    
    def stop(self):
        """ 
        The stop method is called once while the SNAP Desktop application is shutting down. 
        You would put any clean-up code here.
        """
        pass
```

Example code for a SNAP Desktop extension using Jython 
can be found [here](https://github.com/senbox-org/snap-examples/tree/master/snap-jython-examples/snap-desktop-plugins).

#### Plugin registration file

The plugin registration must be named `org.esa.snap.jython.PluginActivator` and must be located in 
the `META-INF/services` subdirectory of your Jython plugin directory or ZIP file. It lists all your plugin 
activator classes using their fully qualified package path. For the example plugin directory above the 
content of the file would be:

`one_plugin.PluginActivator`

`another_plugin.PluginActivator`