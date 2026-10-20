#import "../texture-producer-20261020/native_common.h"

static CGImageRef Load(NSString *path) {
    CGImageSourceRef s=CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path],NULL);
    CGImageRef image=s?CGImageSourceCreateImageAtIndex(s,0,NULL):NULL;
    if(s)CFRelease(s);return image;
}

int main(int argc,char **argv) {
    @autoreleasepool {
        if(argc!=5)return 64;
        NSString *mode=@(argv[1]),*input=@(argv[2]),*argument=@(argv[3]),*output=@(argv[4]);
        CGColorSpaceRef srgb=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
        CIContext *context=[CIContext contextWithOptions:@{}];
        CIImage *result=nil;NSUInteger orientation=1;
        if([mode isEqual:@"orientation"]) {
            orientation=argument.integerValue;
            if(orientation<1||orientation>8)return 64;
            CGImageRef image=Load(input);if(!image)return 1;
            static const int inverse[]={0,1,2,3,4,5,8,7,6};
            result=[[CIImage imageWithCGImage:image] imageByApplyingOrientation:inverse[orientation]];
            CGImageRelease(image);
        } else if([mode isEqual:@"compose"]) {
            result=[CIImage imageWithColor:[CIColor colorWithRed:0 green:0 blue:0 alpha:1]];
            result=[result imageByCroppingToRect:CGRectMake(0,0,1024,512)];
            NSUInteger index=0;
            for(NSString *path in @[input,argument]) {
                CGImageRef image=Load(path);if(!image)return 1;
                VNImageRequestHandler *handler=[[VNImageRequestHandler alloc] initWithCGImage:image options:@{}];
                VNDetectFaceLandmarksRequest *faces=[VNDetectFaceLandmarksRequest new];NSError *error=nil;
                if(![handler performRequests:@[faces] error:&error]||!faces.results.count)return 1;
                VNFaceObservation *face=faces.results[0];
                CGRect b=face.boundingBox;CGFloat width=CGImageGetWidth(image),height=CGImageGetHeight(image);
                CGRect crop=CGRectMake((CGRectGetMidX(b)-b.size.width*1.5)*width,(CGRectGetMidY(b)-b.size.height*1.5)*height,b.size.width*3*width,b.size.height*3*height);
                CIImage *tile=[CIImage imageWithCGImage:image];crop=CGRectIntersection(crop,tile.extent);
                tile=[tile imageByCroppingToRect:crop];
                tile=[tile imageByApplyingTransform:CGAffineTransformMakeTranslation(-crop.origin.x,-crop.origin.y)];
                CGFloat scale=MIN(512/crop.size.width,512/crop.size.height);
                tile=[tile imageByApplyingTransform:CGAffineTransformMakeScale(scale,scale)];
                tile=[tile imageByApplyingTransform:CGAffineTransformMakeTranslation(index*512+(512-crop.size.width*scale)/2,(512-crop.size.height*scale)/2)];
                result=[tile imageByCompositingOverImage:result];index++;CGImageRelease(image);
            }
        } else return 64;
        CGImageRef image=[context createCGImage:result fromRect:result.extent format:kCIFormatRGBA8 colorSpace:srgb];
        CGImageDestinationRef destination=CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:output],[mode isEqual:@"orientation"]?CFSTR("public.tiff"):CFSTR("public.png"),1,NULL);
        CGImageDestinationAddImage(destination,image,(__bridge CFDictionaryRef)@{(__bridge id)kCGImagePropertyOrientation:@(orientation)});
        BOOL success=CGImageDestinationFinalize(destination);CFRelease(destination);CGImageRelease(image);CGColorSpaceRelease(srgb);return success?0:1;
    }
}
