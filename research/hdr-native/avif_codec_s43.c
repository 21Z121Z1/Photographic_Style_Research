/* Synthetic unitless RGB-code experiment. No photograph input. */
#include <avif/avif.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static void need(int ok,const char *msg){if(!ok){fprintf(stderr,"%s\n",msg);exit(3);}}
static void result(avifResult r,const char *where){if(r!=AVIF_RESULT_OK){fprintf(stderr,"%s: %s\n",where,avifResultToString(r));exit(4);}}
int main(int argc,char **argv){
 if(argc!=8)return 2;const uint32_t w=(uint32_t)strtoul(argv[1],0,10),h=(uint32_t)strtoul(argv[2],0,10),bits=(uint32_t)strtoul(argv[3],0,10),matrix=(uint32_t)strtoul(argv[4],0,10);need(w==256&&h==128&&(bits==10||bits==12)&&(matrix==0||matrix==6),"Unexpected declared fixture");
 avifImage *im=avifImageCreate(w,h,bits,AVIF_PIXEL_FORMAT_YUV444);need(im!=NULL,"image allocation");im->colorPrimaries=1;im->transferCharacteristics=13;im->matrixCoefficients=(avifMatrixCoefficients)matrix;im->yuvRange=AVIF_RANGE_FULL;
 avifRGBImage rgb;avifRGBImageSetDefaults(&rgb,im);rgb.format=AVIF_RGB_FORMAT_RGB;rgb.depth=bits;rgb.avoidLibYUV=AVIF_TRUE;result(avifRGBImageAllocatePixels(&rgb),"RGB allocate");FILE *input=fopen(argv[5],"rb");need(input!=NULL,"input open");for(uint32_t y=0;y<h;y++)need(fread(rgb.pixels+y*rgb.rowBytes,2,w*3,input)==w*3,"input short row");need(fgetc(input)==EOF,"input trailing bytes");fclose(input);result(avifImageRGBToYUV(im,&rgb),"RGB to YUV");
 avifEncoder *enc=avifEncoderCreate();need(enc!=NULL,"encoder allocation");enc->codecChoice=AVIF_CODEC_CHOICE_AOM;enc->maxThreads=1;enc->quality=AVIF_QUALITY_LOSSLESS;enc->qualityAlpha=AVIF_QUALITY_LOSSLESS;enc->speed=8;avifRWData data=AVIF_DATA_EMPTY;result(avifEncoderWrite(enc,im,&data),"AV1 lossless encode");FILE *output=fopen(argv[6],"wb");need(output!=NULL,"output open");need(fwrite(data.data,1,data.size,output)==data.size,"output short write");fclose(output);
 avifImage *decoded=avifImageCreateEmpty();avifDecoder *dec=avifDecoderCreate();need(decoded&&dec,"decoder allocation");dec->maxThreads=1;result(avifDecoderReadMemory(dec,decoded,data.data,data.size),"libavif decode");need(decoded->width==w&&decoded->height==h&&decoded->depth==bits,"decoded geometry/depth");avifRGBImage back;avifRGBImageSetDefaults(&back,decoded);back.format=AVIF_RGB_FORMAT_RGB;back.depth=bits;back.avoidLibYUV=AVIF_TRUE;result(avifRGBImageAllocatePixels(&back),"readback allocation");result(avifImageYUVToRGB(decoded,&back),"YUV to RGB");FILE *raw=fopen(argv[7],"wb");need(raw!=NULL,"readback open");for(uint32_t y=0;y<h;y++)need(fwrite(back.pixels+y*back.rowBytes,2,w*3,raw)==w*3,"readback short row");fclose(raw);char codecs[256];avifCodecVersions(codecs);printf("{\"libavif\":\"%s\",\"codecs\":\"%s\",\"bits\":%u,\"matrix\":%u,\"range\":\"full\",\"quality\":100,\"encoder\":\"aom\",\"bytes\":%zu}\n",avifVersion(),codecs,bits,matrix,data.size);
 avifRGBImageFreePixels(&back);avifImageDestroy(decoded);avifDecoderDestroy(dec);avifRWDataFree(&data);avifEncoderDestroy(enc);avifRGBImageFreePixels(&rgb);avifImageDestroy(im);return 0;
}
