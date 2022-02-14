# Paks

> Paks is a developer wrapper for containers 📦️ (in Python)

![docs/assets/img/paks.png](docs/assets/img/paks.png)

⭐️ [Documentation](https://syspack.github.io/paks) ⭐️

With paks you can save the state of your current container, and issue other 
commands to it while developing. For example:

```
# Load my environment "github" that I share between development containers
> #envload github

# Save a new or updated variable to it on the fly!
> #envsave github GITHUB_USER=abetterdinosaur

# Save my running container "ubuntu" to the default "ubuntu-saved" preserving filesystem changes
> #save

# Oops I forgot something about the container. Inspect the config
> #inspect config

# Copy from host to container and back again
> #cp host:PANCAKES.txt CONTAINER-PANCAKES.txt
> #cp CONTAINER-PANCAKES.txt host:FINISHED-PANCAKES.txt

# Get virtual size of running container
> #size
```

All of the above is possible without leaving your container! 🎉️ And more custom commands to
load are under development! The sibling of this library is [syspack/pack](https://github.com/syspack/pack)
which is implemented in Go.

## TODO

- some commands to interact with a registry?
- allow user to define custom commands on fly for container?
- add singularity backend?
- can we create some packaged thing with container, sbom?
- can we add custom config file from remote? pakages? `#load <commandset>`

🚧️ **under development** 🚧️
