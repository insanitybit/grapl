use ::reqwest;
use actix_web::{post, HttpResponse, Responder};
use serde::{
    Deserialize,
    Serialize,
};

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

#[derive(Serialize, Deserialize)]
struct PluginDeleted {
    plugin_to_delete: String,
    message: String,
}

#[derive(Serialize, Deserialize)]
struct PluginObject {
    plugin_name: String,
    time_uploaded: String,
    date_uploaded: String,
}

#[derive(Serialize, Deserialize)]
struct PluginList {
    plugin_list: Vec<PluginObject>
}


#[post("/modelPluginDeployer/deploy")]
pub async fn grapl_model_plugin_deployer(_req: actix_web::web::Json<PostBody>) -> impl Responder {
    HttpResponse::Ok().json(PluginDeployerResp{
       plugin_name: String::from("test_plugin"),
       response: String::from("success"),
   }).await
}


#[post("/modelPluginDeployer/deletePlugin")]
pub async fn delete_plugin(_req: actix_web::web::Json<PostBody>) -> impl Responder{
    HttpResponse::Ok().json(PluginDeleted{
        plugin_to_delete: String::from("test_plugin"),
        message: String::from("success"),
    }).await
}

#[post("/modelPluginDeployer/listPlugins")]
pub async fn list_plugin() -> impl Responder {
    HttpResponse::Ok().json(PluginList{
        plugin_list: vec![PluginObject{
            plugin_name: String::from("test_plugin"),
            time_uploaded: String::from("012023"),
            date_uploaded: String::from("012023"),
        }], // make vec
    }).await
}
