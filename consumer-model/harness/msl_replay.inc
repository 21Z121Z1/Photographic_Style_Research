// Newly compiled SSA model, separate from the untouched Apple consumer oracle.
static void MSLReplay(id renderer,NSString *dir,NSDictionary *call){
 NSString *path=NSProcessInfo.processInfo.environment[@"VM_CONSUMER_MSL"];if(!path)return;
 NSError *err=nil;NSString *source=[NSString stringWithContentsOfFile:path encoding:NSUTF8StringEncoding error:&err];
 id<MTLCommandQueue> queue=[renderer metalCommandQueue];id<MTLDevice> device=queue.device;
 MTLCompileOptions *options=[MTLCompileOptions new];options.fastMathEnabled=YES;
 id<MTLLibrary> library=[device newLibraryWithSource:source options:options error:&err];
 if(!library){[err.description writeToFile:[dir stringByAppendingPathComponent:@"msl-compile-error.txt"]atomically:YES encoding:NSUTF8StringEncoding error:NULL];return;}
 id<MTLComputePipelineState> ps=[device newComputePipelineStateWithFunction:[library newFunctionWithName:@"f1"]error:&err];
 if(!ps){[err.description writeToFile:[dir stringByAppendingPathComponent:@"msl-pipeline-error.txt"]atomically:YES encoding:NSUTF8StringEncoding error:NULL];return;}
 id<MTLTexture> reference=call[@"textures"][@"13"];
 MTLTextureDescriptor *desc=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:reference.pixelFormat width:reference.width height:reference.height mipmapped:NO];desc.storageMode=MTLStorageModePrivate;desc.usage=MTLTextureUsageShaderRead|MTLTextureUsageShaderWrite;
 id<MTLTexture> output=[device newTextureWithDescriptor:desc];
 NSUInteger count=512*17*4*4;id<MTLBuffer> debug=[device newBufferWithLength:count options:MTLResourceStorageModeShared];
 id<MTLCommandBuffer> cb=[queue commandBuffer];id<MTLComputeCommandEncoder> enc=[cb computeCommandEncoder];[enc setComputePipelineState:ps];
 for(NSString *slot in call[@"textures"])[enc setTexture:[slot isEqualToString:@"13"]?output:call[@"textures"][slot] atIndex:slot.integerValue];
 for(NSString *slot in call[@"bytes"]){NSData *data=call[@"bytes"][slot];[enc setBytes:data.bytes length:data.length atIndex:slot.integerValue];}
 for(NSString *slot in call[@"buffers"]){NSDictionary *binding=call[@"buffers"][slot];id<MTLBuffer> b=binding[@"buffer"];NSUInteger offset=[binding[@"offset"]unsignedIntegerValue];
  if(slot.integerValue==1 && b.contents){b=[device newBufferWithBytes:(char*)b.contents+offset length:b.length-offset options:MTLResourceStorageModeShared];offset=0;}
  [enc setBuffer:b offset:offset atIndex:slot.integerValue];
 }
 [enc setBuffer:debug offset:0 atIndex:30];
 NSArray *grid=call[@"grid"],*group=call[@"group"];
 [enc dispatchThreads:MTLSizeMake([grid[0]unsignedIntegerValue],[grid[1]unsignedIntegerValue],1) threadsPerThreadgroup:MTLSizeMake(16,16,1)];
 [enc endEncoding];[cb commit];[cb waitUntilCompleted];
 NSInteger kernelStatus=cb.status;
 if(cb.error){[cb.error.description writeToFile:[dir stringByAppendingPathComponent:@"msl-execution-error.txt"]atomically:YES encoding:NSUTF8StringEncoding error:NULL];return;}
 [[NSData dataWithBytes:debug.contents length:count]writeToFile:[dir stringByAppendingPathComponent:@"msl-checkpoints.f32"]atomically:YES];
 NSUInteger stride=reference.width*8;id<MTLBuffer> read=[device newBufferWithLength:stride*reference.height options:MTLResourceStorageModeShared];cb=[queue commandBuffer];id<MTLBlitCommandEncoder> blit=[cb blitCommandEncoder];[blit copyFromTexture:output sourceSlice:0 sourceLevel:0 sourceOrigin:MTLOriginMake(0,0,0)sourceSize:MTLSizeMake(output.width,output.height,1)toBuffer:read destinationOffset:0 destinationBytesPerRow:stride destinationBytesPerImage:stride*output.height];[blit endEncoding];[cb commit];[cb waitUntilCompleted];
 [[NSData dataWithBytes:read.contents length:read.length]writeToFile:[dir stringByAppendingPathComponent:@"msl-output.f16"]atomically:YES];
 NSDictionary *meta=@{@"shape":@[@(output.height),@(output.width),@4],@"dtype":@"<f2",@"checkpoints_shape":@[@512,@17,@4],@"scope":@"newly compiled SSA model, separate Apple output is oracle",@"device":device.name,@"command_status":@(kernelStatus),@"grid":grid,@"max_threads":@(ps.maxTotalThreadsPerThreadgroup),@"execution_width":@(ps.threadExecutionWidth)};[[NSJSONSerialization dataWithJSONObject:meta options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:[dir stringByAppendingPathComponent:@"msl.json"]atomically:YES];
 ps=[device newComputePipelineStateWithFunction:[library newFunctionWithName:@"sentinel"]error:&err];cb=[queue commandBuffer];enc=[cb computeCommandEncoder];[enc setComputePipelineState:ps];[enc setTexture:output atIndex:13];[enc setBuffer:debug offset:0 atIndex:30];[enc dispatchThreads:MTLSizeMake(reference.width,reference.height,1)threadsPerThreadgroup:MTLSizeMake(16,16,1)];[enc endEncoding];[cb commit];[cb waitUntilCompleted];
 [[NSData dataWithBytes:debug.contents length:count]writeToFile:[dir stringByAppendingPathComponent:@"sentinel-checkpoints.f32"]atomically:YES];
}
