jconfigure
==========

jconfigure is a package for configuring a python project with a dictionary created by parsing a number of
configuration files and merging them. The application uses environment variables to locate config files on
disk and to choose which files to read.

The really useful thing about this library is the yaml parser, as it implements a number of custom tags
which are documented below that allow you to read in information such as environment variables, as well
as including other files. This is useful, for instance for me, where in production, my secrets are stored
as environment variables or in text files in the filesystem, and I can write files like this:

```
aws_config: !IncludeYaml /var/lib/app/config/aws.yaml
databases:
  - host: mysql
    username: !IncludeText /var/lib/app/config/user-name
    password: !IncludeText
      filename: !JoinFilePaths
        - !EnvVar SECRETS_VOLUME_PATH
        - database-password
```

And get a config that looks like this:
```
aws_config:
  aws_access_key_id: access
  aws_secret_access_key: secret

databases:
  - host: mysql
    username: root
    password: root
```

## Configuration Process
You call into the configuration process with jconfigure by using the `jconfigure.configure`
method. You can provide a number of options to this to override default behaviors, but basically
there are three phases to the configuration process:

* Configure Logging
* Configure From defaults files
* Configure From Active Profile files

Each of these steps is exactly the same process, but in each case, the parser is looking for different files.
What happens in each case is that jconfigure uses the `JCONFIGURE_CONFIG_DIRECTORIES` environment variable, which
should be a comma seperated list of directory names to search for config files. If nothing is set, it
defaults to using a single directory, `$(pwd)/config`. It then looks for config files that match the filenames
being searched for in each directory, and merges all of those files, with the config loaded from files in later
directories overriding the configuration from the earlier files.

* In the configure logging step, each directory is searched for `logging.{extension}` files. This
  filename can be overridden
* In the defaults step, each directory is searched for `defaults.{extension}` files. This filename
  can be overridden
* In the active profiles step, each directory is searched for `{profile}.{extension}` files, where profile
  is substituted by one of the configured "active profiles". These profiles are configured with
  the `JCONFIGURE_ACTIVE_PROFILES` environment variable, again a comma seperated list, and the config
  of profiles later in the list overrides the config of the earlier profiles

### Example:
Let's say that I have the following directory structure and environment variables:
```
$ env | grep -e "^JCONFIGURE_"
JCONFIGURE_ACTIVE_PROFILES=prod,overrides
JCONFIGURE_CONFIG_DIRECTORIES=/var/lib/app/config,/var/lib/extra/config

$ ls -R /var/lib/app/config
logging.yaml
defaults.json
test.yaml
stage.yaml
prod.yaml
overrides.yaml

$ ls -R /var/lib/extra/config
prod.yaml
overrides.json
```

First logging would be configured, then the application config would be generated by parsing and merging
the configuration of the following files in order, where you can think of items further down the list
as having precedence:

* /var/lib/app/config/defaults.json
* /var/lib/app/config/prod.yaml
* /var/lib/extra/config/prod.yaml
* /var/lib/app/config/overrides.yaml
* /var/lib/extra/config/overrides.json

As you can see, the parser is pretty agnostic to the filetype, so far it knows how to parse either json
or yaml files, and yes, yaml files can end `.yml`, but please just don't. The point is that it only cares
about the name of the file without the extension with regards to whether the file will be parsed, and
if there isn't an active profile, files like `test.yaml` and `stage.yaml` won't be parsed.

The last thing about file extensions you should be aware of is that you are allowed to have multiple
files of the same name and different extension in a directory. Like so:
```
$ ls -R /var/lib/app/config
defaults.json
defaults.yaml
```

Both files will be parsed, and overridden as normal, but the ordering of which file extension is parsed
first is not defined and you should not rely on it.

## Yaml Tags
This section documents the custom Yaml Tags and how you can call them. For all of the tags that include
other files, the include is relative, so if the file to be included is in the same directory as the file
including it you can use:
```
include_json_file: !IncludeJson otherfile.json
```

### !ContextValue
This returns the value associated with the provided key supplied in the _context_ argument to `configure`. It allows
for a default value to be passed in the case that the context key isn't set. If the default
is not provided and there is no such key provided in the context, will throw an exception.

Usage:
```
context_scalar: !ContextValue cli_log_level
context_mapping: !ContextValue
  key: cli_log_level

context_default: !ContextValue
  key: cli_log_level
  default: INFO
```

### !EnvVar
This returns the string value of the passed environment variable name, the mapping form of this allows
for a default value to be passed in the case that the environment variable isn't set. If the default
is not provided and the environment variable isn't set, will throw an exception

Usage:
```
env_var_scalar: !EnvVar DATABASE_PASSWORD
env_var_mapping: !EnvVar
  name: DATABASE_PASSWORD

env_var_default: !EnvVar
  name: DATABASE_MASTER_PASSWORD
  default: null
```

### !StringFormat
This tag takes a list or mapping specifying a format string and arguments for formatting and
returns the formatted string:

Usage:
```
format_sequence_one: !StringFormat
  - echo is a {}
  - [cat]

format_sequence_two: !StringFormat
  - echo is a {} and oscar is a {}
  - [cat, dog]

format_sequence_two_kw: !StringFormat
  - echo is a {animal_one} and oscar is a {animal_two}
  - animal_one: cat
    animal_two: dog

format_mapping_one: !StringFormat
  string: echo is a {}
  format_args: [cat]

format_mapping_two: !StringFormat
  string: echo is a {} and oscar is a {}
  format_args: [cat, dog]

format_mapping_two_kw: !StringFormat
  string: echo is a {animal_one} and oscar is a {animal_two}
  format_args:
    animal_one: cat
    animal_two: dog

# If no format args are provided in the sequence or mapping form, simply returns the string
format_sequence_null_case: !StringFormat
  - echo is a cat

format_mapping_null_case: !StringFormat
  string: echo is a cat
```

### !IncludeJson
This parses a relative json file and returns the parsed dictionary

Usage:
```
include_json_scalar: !IncludeJson filename.json
include_json_mapping: !IncludeJson
  filename: filename.json
```

### !IncludeText
This parses a relative text file and returns the whitespace trimmed string

Usage:
```
include_json_scalar: !IncludeText /var/lib/secrets/database-password
include_json_mapping: !IncludeText
  filename: /var/lib/secrets/database-password
```

### !IncludeYaml
This parses a relative yaml file and returns the parsed dictionary, the yaml file that
is included is parsed in the same way the current file is being parsed, using the same
custom tags, so you can include a file, and it can include other files, etc.

Usage:
```
include_yaml_scalar: !IncludeYaml filename.yaml
include_yaml_mapping:
  filename: !IncludeYaml filename.yaml
```

### !JoinFilePaths
This tag takes a list or a mapping with a key "paths" that is a list, and simply
joins all of those file paths together, returning the string path. The rules of how
this joining works are the same as python's `os.path.join`.

Usage:
```
join_file_paths_sequence: !IncludeYaml
  filename: !JoinFilePaths
    - !EnvVar SECRETS_DIR_PATH
    - database-secrets.yaml

join_file_paths_mapping: !IncludeYaml
  filename: !JoinFilePaths
    paths:
      - !EnvVar SECRETS_DIR_PATH
      - database-secrets.yaml
```

### !Chain
This tag takes a list of lists and chains them together into a single list

Usage:
```
chain_sequence: !Chain
  - [1, 2]
  - [3, 4, 5]

chain_mapping: !Chain
  lists:
    - [1, 2]
    - [3, 4, 5]
```

### !Timestamp
This tag takes an optional date/datetime and format and produces a timestamp in the format.
If the format is not supplied, ISO format is used, and if the timestamp is not provided, utcnow
is used. The tag also takes an optional "delta" key that should be a dictionary that
can be passed as kwargs to the `datetime.timedelta` constructor. This diff will be added to the
time or date provided before the timestamp is produced.

Usage:
```
utc_now_iso: !Timestamp {}

utc_now_condensed: !Timestamp
  format: "%y%m%d%H%M%S"

day_iso: !Timestamp
  time: 2018-06-23

day_condensed: !Timestamp
  time: 2018-06-23
  format: "%y%m%d"

time_iso: !Timestamp
  time: 2018-06-23 23:23:23

time_condensed: !Timestamp
  time: 2018-06-23 23:23:23
  format: "%y%m%d%H%M%S"

year_later_day_iso: !Timestamp
  time: 2018-06-23
  delta:
    years: 1
    seconds: 23

week_ago_date: !Timestamp
  time: 2018-06-23
  format: "%y%m%d"
  delta:
    days: -7

week_ago_iso: !Timestamp
  delta:
    days: -7
```
