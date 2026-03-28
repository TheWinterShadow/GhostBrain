# Infrastructure

This page documents the underlying Terraform module (`modules/ghost_brain`) that deploys the GhostBrain architecture.

<!-- BEGIN_TF_DOCS -->
# Infrastructure Details



## Inputs
## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_caller_id"></a> [allowed\_caller\_id](#input\_allowed\_caller\_id) | Allowed caller ID to whitelist | `string` | `""` | no |
| <a name="input_bucket_name_prefix"></a> [bucket\_name\_prefix](#input\_bucket\_name\_prefix) | Prefix for the GCS bucket name. | `string` | n/a | yes |
| <a name="input_cloud_run_image"></a> [cloud\_run\_image](#input\_cloud\_run\_image) | Container image URI for the Cloud Run service. | `string` | n/a | yes |
| <a name="input_deepgram_api_key"></a> [deepgram\_api\_key](#input\_deepgram\_api\_key) | Deepgram API Key | `string` | n/a | yes |
| <a name="input_ghost_brain_service_name"></a> [ghost\_brain\_service\_name](#input\_ghost\_brain\_service\_name) | Name of the Cloud Run service. | `string` | n/a | yes |
| <a name="input_groq_api_key"></a> [groq\_api\_key](#input\_groq\_api\_key) | Groq API Key | `string` | n/a | yes |
| <a name="input_openai_api_key"></a> [openai\_api\_key](#input\_openai\_api\_key) | OpenAI API Key | `string` | n/a | yes |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | GCP region. | `string` | n/a | yes |
| <a name="input_system_instructions"></a> [system\_instructions](#input\_system\_instructions) | System instructions for the AI personality | `string` | `""` | no |
| <a name="input_twilio_account_sid"></a> [twilio\_account\_sid](#input\_twilio\_account\_sid) | Twilio Account SID | `string` | n/a | yes |
| <a name="input_twilio_auth_token"></a> [twilio\_auth\_token](#input\_twilio\_auth\_token) | Twilio Auth Token | `string` | n/a | yes |

## Outputs
## Outputs

| Name | Description |
|------|-------------|
| <a name="output_bucket_name"></a> [bucket\_name](#output\_bucket\_name) | Name of the transcript GCS bucket. |
| <a name="output_cloud_run_url"></a> [cloud\_run\_url](#output\_cloud\_run\_url) | Public URL of the Cloud Run service. |
| <a name="output_twilio_application_sid"></a> [twilio\_application\_sid](#output\_twilio\_application\_sid) | The SID of the Twilio Application created for Ghost Brain. |
<!-- END_TF_DOCS -->
