from fastapi import APIRouter
from api.v1.routes import user_route as users
from api.v1.routes import merchant_routes as merchants
from api.v1.routes import referral_route as referrals
from api.v1.routes import authentication_routes as authentication
from api.v1.routes import mpin_routes as mpin
from api.v1.routes import transaction_routes as transactions
from api.v1.routes import kyc_routes as kyc
from api.v1.routes import qr_routes as qr
from api.v1.routes import payQR_routes as pay_qr


from api.v1.routes import unilevel_routes

router = APIRouter()


router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
router.include_router(authentication.router, prefix="", tags=["authentication"])
router.include_router(mpin.router, prefix="/mpin", tags=["mpin"])
router.include_router(transactions.router, prefix="", tags=["transactions"])
router.include_router(kyc.router, prefix="/kyc", tags=["kyc"])
router.include_router(qr.router, prefix="/qr", tags=["qr"]),
router.include_router(pay_qr.router, prefix="/payqr", tags=["pay-qr"])

router.include_router(unilevel_routes.router, prefix="/unilevel", tags=["unilevel"])