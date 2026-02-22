local CustomHeaderHandler = {
  PRIORITY = 1000,
  VERSION = "0.1",
}

function CustomHeaderHandler:access(conf)
  kong.service.request.set_header("X-Custom-Auth-Gateway", "Kong-OSS")
end

return CustomHeaderHandler
