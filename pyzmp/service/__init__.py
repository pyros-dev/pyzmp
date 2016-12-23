# This package contains the service/provider duality
# Multiple provider implementation are possible, depending on your system configuration

# The protocol is not specified here. Any protocol could fulfill the requirements to implement services

# Different synchronicity paradigm & control flows are possible, and this subpackage only focus on that aspect.

from .service import Service, services, discover, ServiceCallTimeout