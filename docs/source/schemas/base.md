# base

Base schema from which community specific schemas are built.

### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| custom_fields | `object` | ✅ | object |  | Block for custom data. |
| custom_fields.dsmd | `array` | ✅ | object |  | Domain specific metadata (dsmd). |
| metadata | `object` | ✅ | object |  | Resource metadata. |
| metadata.title | `string` | ✅ | string |  | Title of resource. |
| metadata.description | `string` | ✅ | string |  | Summary of resource. |
| metadata.creators | `array` | ✅ | object |  | List of creators. |
| metadata.creators[].affiliations | `array` |  | object |  | Member affiliations. |
| metadata.creators[].affiliations[].name | `string` | ✅ | string |  | Name of institution. |
| metadata.creators[].person_or_org | `object` | ✅ | object |  | Person or organisation. |
| metadata.creators[].person_or_org.name | `string` |  | string |  | Full set of given names. |
| metadata.creators[].person_or_org.family_name | `string` |  | string |  | Family name(s). |
| metadata.creators[].person_or_org.given_name | `string` |  | string |  | Given name(s). |
| metadata.creators[].person_or_org.identifiers | `array` |  | object and/or object |  | ORCIDs or other IDs |
| metadata.creators[].person_or_org.type | `const` | ✅ | `personal` |  | Personal or organisation. |
| metadata.rights | `array` | ✅ | object |  | Rights or license. |
| metadata.rights[].id | `const` | ✅ | `cc-by-4.0` |  | ID of rights or license. |
| metadata.resource_type | `object` | ✅ | object |  | Type of resource. |
| metadata.resource_type.id | `const` | ✅ | `model` |  | Resource class. |
| metadata.subjects | `array` |  | object | `[]` | List of keywords defining subjects resource covers. |
| metadata.subjects[].subject | `string` | ✅ | string |  | Subject keyword. |
| metadata.version | `string` | ✅ | [`^v\d+(\.\d+)*`](https://regex101.com/?regex=%5Ev%5Cd%2B%28%5C.%5Cd%2B%29%2A) |  | Current version of resource. |
| metadata.publisher | `string` |  | string |  | Publisher of resource. |
| metadata.publication_date | `None` |  | None |  | Date of publication of resource. |
| metadata.identifiers | `array` |  | object and/or object |  | Resource identifiers such as ORCID or DOI. |
| access | `object` |  | object | `{"files": "public", "record": "public"}` | Accessibility of data outside of owners. |
| access.embargo | `object` |  | object |  | Details of resource embargo. |
| access.embargo.active | `boolean` | ✅ | boolean |  | Whether resource is under embargo. |
| access.embargo.reason | `string` or `null` | ✅ | string |  | Cause for embargo. |
| access.files | `None` |  | `public` `private` | `"public"` | Accessibility to individual files. |
| access.record | `None` |  | `public` `private` | `"public"` | Accessibility to record as a whole. |
| access.status | `None` |  | `open` `closed` |  | Current status or resource. |
| files | `object` |  | object |  | Details of files. |
| files.enabled | `boolean` | ✅ | boolean |  | Whether file is enabled. |
| community | `string` |  | [`\d{8}-(\d{4}-){3}\d{12}`](https://regex101.com/?regex=%5Cd%7B8%7D-%28%5Cd%7B4%7D-%29%7B3%7D%5Cd%7B12%7D) |  | UUID of community associated with resource. |
