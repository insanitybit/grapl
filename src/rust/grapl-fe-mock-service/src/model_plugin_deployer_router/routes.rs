use ::reqwest;
use actix_web::{post, HttpResponse, Responder};
use serde::{
    Deserialize,
    Serialize,
};

use crate::{
    make_request,
};
// use actix_web::web::Json;

#[derive(Serialize, Deserialize)]
pub struct DeployRequest {
    name: String,
}

#[derive(thiserror::Error, Debug)]
pub enum PluginError {
    #[error("Request Error")]
    RequestError(#[from] reqwest::Error),

    #[error("Invalid schema contents")]
    InvalidSchema,

    #[error("Unable to read schema contents")]
    ReadError,

    #[error("Internal Server Error")]
    ServerError,
}

// accept http requests, translate to grpc requests.
#[derive(Serialize, Deserialize)]
pub struct PluginDeployerResp {
    plugin_name: String,
    response: String,
}

#[derive(Serialize, Deserialize)]
pub struct PostBody {
    body: String
}

    // struct PluginSuccessfullyDeleted {
    //     plugin_to_delete: String,
    //     message: Boolean,
    // }


#[post("/modelPluginDeployer/deploy")]
pub async fn grapl_model_plugin_deployer(_req: actix_web::web::Json<PostBody>) -> impl Responder {
    HttpResponse::Ok().json(PluginDeployerResp{
       plugin_name: String::from("test_plugin"),
       response: String::from("success"),
   }).await
}


// #[post("/modelPluginDeployer/deletePlugin")]
// pub async fn delete_plugin(body: Json<PostBody>) -> Result<web::Json<PluginSuccessfullyDeleted>, E> {
//     Ok(web::Json(PluginSuccessfullyDeleted{
//         plugin_to_delete: String::from("test_plugin"),
//         message: String::from("success"),
//     }))
// }

// actix procedural macros that route incoming http requests
#[post("/modelPluginDeployer/listPlugins")]
pub async fn list_plugin() -> impl Responder {
    let response = make_request("listPlugins").await;

    match response {
        Ok(response) => HttpResponse::Ok().json(response),

        Err(PluginError::InvalidSchema) => HttpResponse::BadRequest().finish(),

        Err(PluginError::ReadError) => HttpResponse::Conflict().finish(),

        Err(PluginError::ServerError) => HttpResponse::BadRequest().finish(),

        Err(PluginError::RequestError(_)) => HttpResponse::InternalServerError().finish(),
    }
}
