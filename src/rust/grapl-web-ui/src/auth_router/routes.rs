use ::reqwest;
use actix_web::{
    get,
    HttpResponse,
    Responder,
};
use serde::{
    Deserialize,
    Serialize,
};

use crate::login_request_with_body;

#[derive(Serialize, Deserialize)]
pub struct LoginBody {
    username: String,
    password: String,
}

#[derive(thiserror::Error, Debug)]
pub enum AuthError {
    #[error("Request Error")]
    RequestError(#[from] reqwest::Error),

    #[error("Invalid creds")]
    InvalidCreds,
}

struct LoginResp{
    message: String,
}

#[get("/login")]
pub async fn grapl_login(_req: actix_web::web::Json<LoginBody>) -> impl Responder {
    HttpResponse::Ok().json(
        LoginResp{
            message: String::from("success"),
        }
    )
}
