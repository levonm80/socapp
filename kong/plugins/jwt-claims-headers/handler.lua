local BasePlugin = require "kong.plugins.base_plugin"

local JwtClaimsHeadersHandler = BasePlugin:extend()

JwtClaimsHeadersHandler.PRIORITY = 999
JwtClaimsHeadersHandler.VERSION = "1.0.0"

function JwtClaimsHeadersHandler:new()
  JwtClaimsHeadersHandler.super.new(self, "jwt-claims-headers")
end

function JwtClaimsHeadersHandler:access(conf)
  JwtClaimsHeadersHandler.super.access(self)
  
  -- Get JWT claims from context (set by JWT plugin)
  local jwt_claims = kong.ctx.shared.jwt_claims
  
  if jwt_claims and jwt_claims.sub then
    -- Add X-User-Id header with the subject claim
    kong.service.request.set_header("X-User-Id", jwt_claims.sub)
  end
end

return JwtClaimsHeadersHandler

