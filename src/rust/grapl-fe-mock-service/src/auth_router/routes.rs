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

// use crate::login_request_with_body;

#[derive(Serialize, Deserialize)]
pub struct LoginBody {
    username: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
pub struct LoginResp{
    message: String,
    jwt: String
}


#[derive(thiserror::Error, Debug)]
pub enum AuthError {
    #[error("Request Error")]
    RequestError(#[from] reqwest::Error),

    #[error("Invalid creds")]
    InvalidCreds,
}

#[get("/login")]
pub async fn grapl_login() -> impl Responder {
    HttpResponse::Ok().json(LoginResp{
        message: String::from("success"),
        jwt: String::from("CiAjmNcv20")
    })
}
