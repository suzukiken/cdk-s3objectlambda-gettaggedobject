import * as cdk from '@aws-cdk/core';
import * as s3 from '@aws-cdk/aws-s3'
import * as iam from "@aws-cdk/aws-iam";
import * as lambda from "@aws-cdk/aws-lambda";
import { PythonFunction } from "@aws-cdk/aws-lambda-python";

export class Cdks3ObjectlambdaGettaggedobjectStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const STACK_NAME = id.toLocaleLowerCase().replace('stack', '')
    
    const bucket = new s3.Bucket(this, 'bucket', {
      bucketName: STACK_NAME + '-bucket',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      versioned: true
    })
    
    const accesspoint = new s3.CfnAccessPoint(this, "accesspoint", {
      bucket: bucket.bucketName,
      name: STACK_NAME + '-accesspoint',
    })
    
    const role = new iam.Role(this, "role", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      roleName: STACK_NAME + "-role",
    });
    
    const statement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
    });

    statement.addActions("s3-object-lambda:WriteGetObjectResponse");
    statement.addResources("arn:aws:s3-object-lambda:ap-northeast-1:" + this.account + ":accesspoint/*")

    const policy = new iam.Policy(this, "policy", {
      policyName: STACK_NAME + "-policy",
      statements: [statement],
    });

    role.attachInlinePolicy(policy);
    
    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        "service-role/AWSLambdaBasicExecutionRole"
      )
    );
    
    const lambda_function = new PythonFunction(this, "lambda_function", {
      entry: "lambda",
      index: "index.py",
      handler: "lambda_handler",
      functionName: STACK_NAME + '-function',
      runtime: lambda.Runtime.PYTHON_3_8,
      timeout: cdk.Duration.seconds(60),
      role: role,
      environment: {
        BUCKET_NAME: bucket.bucketName
      }
    });
    
    bucket.grantRead(lambda_function)
    
    new cdk.CfnOutput(this, "output_bucket", {
      value: bucket.bucketName
    })
    
    new cdk.CfnOutput(this, "output_lambda", {
      value: lambda_function.functionArn
    })
  }
}
