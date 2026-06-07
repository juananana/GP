from app.runtime.gateway_registry import TENANT_GATEWAYS


def register_tenant_routes(router):
    for tenant, entry in TENANT_GATEWAYS.items():
        if entry["processor"] == "acmepay":
            router.post(f"/tenants/{tenant}/payments", handle_legacy_tenant_payment)


def handle_legacy_tenant_payment(request):
    return {"ok": True}

