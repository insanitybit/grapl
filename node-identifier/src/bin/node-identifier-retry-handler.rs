extern crate grapl_config;
extern crate lambda_runtime as lambda;
extern crate node_identifier;
extern crate rusoto_core;
extern crate rusoto_s3;
extern crate rusoto_sqs;
extern crate rusoto_dynamodb;
extern crate simple_logger;

use log::{info, error};
use std::time::Duration;

use node_identifier::{retry_handler, local_handler, init_s3_client, init_sqs_client, init_dynamodb_client};

use lambda::lambda;
use rusoto_core::RusotoError;
use rusoto_s3::S3;
use rusoto_sqs::{Sqs, ListQueuesRequest};
use rusoto_dynamodb::DynamoDb;
use tokio::runtime::Runtime;

// fn main() {
//     simple_logger::init_with_level(log::Level::Info).unwrap();
//     lambda!(retry_handler);
// }


fn main() -> Result<(), Box<dyn std::error::Error>> {
    simple_logger::init_with_level(grapl_config::grapl_log_level())
        .expect("Failed to initialize logger");

    let is_local = std::env::var("IS_LOCAL")
        .is_ok();

    if is_local {
        info!("Running locally");
        let mut runtime = Runtime::new().unwrap();

        let s3_client = init_s3_client();
        loop {
            if let Err(e) = runtime.block_on(s3_client.list_buckets()) {
                match e {
                    RusotoError::HttpDispatch(_) => {
                        info!("Waiting for S3 to become available");
                        std::thread::sleep(Duration::new(2, 0));
                    },
                    _ => break
                }
            } else {
                break;
            }
        }

        let sqs_client = init_sqs_client();
        loop {
            if let Err(e) = runtime.block_on(
                sqs_client.list_queues(ListQueuesRequest{ queue_name_prefix: None })
            ) {
                match e {
                    RusotoError::HttpDispatch(_) => {
                        info!("Waiting for SQS to become available");
                        std::thread::sleep(Duration::new(2, 0));
                    },
                    _ => break
                }
            }
        }

        let dynamodb_client = init_dynamodb_client();
        loop {
            if let Err(e) = runtime.block_on(dynamodb_client.describe_endpoints()) {
                match e {
                    RusotoError::HttpDispatch(_) => {
                        info!("Waiting for DynamoDB to become available");
                        std::thread::sleep(Duration::new(2, 0));
                    },
                    _ => break
                }
            }
        }

        loop {
            if let Err(e) = runtime.block_on(async move { local_handler(false).await }) {
                error!("{}", e);
            }

            std::thread::sleep_ms(2_000);
        }
    }  else {
        info!("Running in AWS");
        lambda!(retry_handler);
    }
    Ok(())
}
