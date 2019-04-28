# 内容归档

## 构建相关
### Xcode10上如何自定义引擎构建

[Supporting legacy platforms](https://github.com/flutter/flutter/wiki/Supporting-legacy-platforms)

## 工具链

## 文档

## C++支持

## 反射支持

## 包大小优化

## 性能调优

## 符号化

Android：

参见:script/android_engine_symbolicate.py(-h获取具体用法)

## 自定义构建替换flutter自带的snapshots
目前在flutter/bin/cache/dart-sdk/bin/snapshots目录下，存在多个flutter自带的snapshots。
```
如用于分析的analysis_server.dart.snapshot，dartanalyzer.dart.snapshot;
用于文档的dartfmt.dart.snapshot;
用于格式化的dartfmt.dart.snapshot;
用于kernel-service的kernel-service.dart.snapshot;
用于依赖获取的pub.dart.snapshot;
```
那么当我们需要去修改的时候，如何处理呢？
请使用: script/get_dartsdk_for_flutter.py

例如，需要修改用于IDE代码分析的analysis_server.dart.snapshot，则可以通过
```
get_dartsdk_for_flutter.py -fp your-flutter-root-path
```
这个脚本将会根据你的flutter环境中的依赖关系，获取具体的dartsdk依赖，然后重新生成相应的snapshot，替换即可。
当需要编辑相应源代码的时候，找到对应的package，fork出来修改，替换，使用脚本重新编译(修改会被保留，因而生效)重新编译构建snapshot，替换即可。

## Patches (stable_v1.0)

兼容性问题

### HUAWEI P6-T00 Android 4.2.2, API 17
#### 问题
Flutter页面黑并且Crash
#### 错误日志:
```
[ERROR:flutter/shell/platform/android/android_context_gl.cc(187)] Could not create an EGL context[ERROR:flutter/shell/platform/android/android_context_gl.cc(53)] EGL Error: EGL_BAD_MATCH (12297)
```
#### 问题分析:
此款设备上OpenGL driver支持有问题，造成share context创建失败。

#### 解决方案:
在engine(engine/src/flutter)中添加错误时的容错逻辑(不会影响之前正常的设备)。参见:
patches/stable_v1.0/engine#src#flutter/0005-Workaround-for-android-eglCreateContext-fai.patch

#### 问题跟踪:
https://github.com/flutter/engine/pull/6358

### Xiaomi MI PAD 2 Android5.1 API 22
#### 问题1
黑屏并且Crash
#### 错误日志
```
[ERROR:flutter/shell/gpu/gpu_surface_gl.cc(55)] Failed to setup Skia Gr context.
```
#### 问题分析:
此款设备上OpenGL driver支持有问题，造成skia中的验证逻辑因为GL_EXT_texture_buffer支持不完备而失败。

#### 解决方案:
移除skia(engine/src/third_party/skia)中对于GL_EXT_texture_buffer的判断逻辑，因为flutter中已不需要。参见:
patches/stable_v1.0/engine#src#third_party#skia/0001-Workaround-for-Flutter-related-black-screen.patch

#### 问题跟踪
https://github.com/flutter/flutter/issues/22353

#### 问题2
页面内容部分展示后，图片下载网络请求过程中奔溃

#### 错误日志
```
00  pc 00c20310  /data/app/xxx/lib/arm/libflutter.so
--- --- ---
00 pc 00c20310  /data/app/com.taobao.idlefish.debug-1/lib/arm/libflutter.so
01 pc 00bc6ee7  /data/app/com.taobao.idlefish.debug-1/lib/arm/libflutter.so
符号化:src kylewong$ ./third_party/android_tools/ndk/toolchains/arm-linux-androideabi-4.9/prebuilt/darwin-x86_64/bin/arm-linux-androideabi-addr2line -e ./out/android_release_unopt/libflutter.so
00c20310
linux-atomic.c:?
00c20310
linux-atomic.c:?
00bc6ee7
/Users/kylewong/Codes/Flutter/beta/engine/src/out/android_release_unopt/../../third_party/boringssl/src/crypto/fipsmodule/cipher/e_aes.c:312
```
#### 问题分析:
此款设备是Intel的Atom处理器，openSSL中的相关逻辑对其判断有问题，导致指令集支持判断失败导致奔溃。
#### 解决方案
在openssl中(engine/src/third_party/boringssl/src)添加对于此种处理器的处理逻辑。参见:
patches/stable_v1.0/engine#src#third_party#boringssl#src/0001-Add-intel-emulation-layer-logic-for-arm.patch

### HUAWEI H30-T00 Android 4.2.2 API 17
#### 问题
Flutter页面黑并且Crash
#### 错误日志:
```
[ERROR:flutter/shell/gpu/gpu_surface_gl.cc(55)] Failed to setup Skia Gr context.
```
#### 问题分析:
此款设备上OpenGL driver支持有问题，造成skia中的验证逻辑因为GL_EXT_debug_marker支持不完备而失败。参阅https://www.khronos.org/registry/OpenGL/extensions/EXT/EXT_debug_marker.txt
GL_EXT_debug_marker用于debug/profile时，用来改善OpenGL & OpenGL ES 开发工具中的用户体验。去除此段逻辑，对于Release模式没有影响，对于Debug/Profile模式，最多是性能诊断的时候，部分机型，可能会发生部分API在被调用时不支持导致异常的问题。

#### 解决方案:
移除skia(engine/src/third_party/skia)中对于GL_EXT_debug_marker的判断逻辑。参见:
patches/stable_v1.0/engine#src#third_party#skia/0001-Workaround-for-Flutter-related-black-screen.patch

### iOS上手势问题引起的flutter状态异常
#### 问题
Flutter页面点击事件在某些场景下失效
#### 错误现象
在某些场景下，如当Flutter页面与Native嵌套使用的时候，Flutter页面ListView中带小图可以点击查看大图(Push Native的ViewController展示)，大图上单击可以退出Native页面。这种场景下，连续两个手指点击会造成Flutter页面最后滑动异常，表现为页面卡顿或者点击事件不生效。

#### 问题分析
Flutter在iOS上的手势处理，数据来源于FlutterViewController的touchesBegan/touchesMoved/touchesEnded/touchesCancelled这四个函数。一个触摸事件的正常与结束，取决于开始(touchesBegan)同结束(touchesEnded/touchesCancelled)的对称关系。然而，在此种场景下，这种对称关系被破坏了。

#### 解决方案:
在engine(engine/src/flutter)中添加容错逻辑。参见:
patches/stable_v1.0/engine#src#flutter/0002-Fix-a-tap-failure-problem-when-double-click.patch

#### 问题跟踪
https://github.com/flutter/engine/pull/6145

稳定性问题

### iOS上后台GPU渲染crash
#### 崩溃日志
```
Exception Type: SIGSEGV
Exception Codes: SEGV_ACCERR at 0x1
Triggered by Thread: 24

Thread 24 Crashed:
0 libGPUSupportMercury.dylib 0x000000018b1d1f90 _gpus_ReturnNotPermittedKillClient :12 (in libGPUSupportMercury.dylib)
1 GLEngine 0x0000000185d691f4 0x0000000185c78000 + 987636
2 GLEngine 0x0000000185d690f8 0x0000000185c78000 + 987384
3 OpenGLES 0x0000000185d77c58 -[EAGLContext presentRenderbuffer:] :72 (in OpenGLES)
4 Flutter 0x0000000103a75de8 0x0000000103a54000 + 138728
5 Flutter 0x0000000103a7880c 0x0000000103a54000 + 149516
6 Flutter 0x0000000103aa7744 0x0000000103a54000 + 341828
7 Flutter 0x0000000103aa7c34 0x0000000103a54000 + 343092
8 Flutter 0x0000000103aa7fd0 0x0000000103a54000 + 344016
9 Flutter 0x0000000103aa7acc 0x0000000103a54000 + 342732
10 Flutter 0x0000000103aab4a0 0x0000000103a54000 + 357536
11 Flutter 0x0000000103a82968 0x0000000103a54000 + 190824
12 Flutter 0x0000000103a83884 0x0000000103a54000 + 194692
```
#### 问题分析:
Flutter Engine实例对应了四个TaskRunner:Platform, UI, GPU 和IO，涉及到直接GPU操作的是GPU和IO，目前的Message Loop下未能彻底保证后台无GPU/IO操作。

#### 解决方案:
在engine(engine/src/flutter)中添加前后台切换时对于TaskRunner的暂停/开始操作(从灰度/上线效果看，有效降低了其造成的crash率)。参见:
patches/stable_v1.0/engine#src#flutter/0003-A-workaround-for-libgpu-related-crash-in-ba.patch

###iOS上内存abort问题
#### 崩溃现象：
连续打开多个Flutter页面(页面上有大量的图片视频等内存占用高的对象)时，iPhone 6Plus等设备上很容易因为内存原因崩溃。

#### 解决方案:
在engine(engine/src/flutter)中添加页面切换时dart垃圾收集的调用机制。参见:
patches/stable_v1.0/engine#src#flutter/0004-Add-notify-idle-api-for-engine-by-Fuju.patch

###iOS上accessibility析构相关crash(最新master已修复)
#### 崩溃日志：
```
Exception Type:  SIGSEGV
Exception Codes: SEGV_ACCERR at 0x9e65bee10
Triggered by Thread:  0
Thread 0 Crashed:
0   libobjc.A.dylib                 0x0000000187587ca8 _objc_release
1   libobjc.A.dylib                 0x0000000187589b9c __ZN12_GLOBAL__N_119AutoreleasePoolPage3popEPv
2   CoreFoundation                  0x00000001883268f4 ___CFRUNLOOP_IS_CALLING_OUT_TO_A_TIMER_CALLBACK_FUNCTION__
3   CoreFoundation                  0x0000000188326624 ___CFRunLoopDoTimer
4   CoreFoundation                  0x0000000188325e58 ___CFRunLoopDoTimers
5   CoreFoundation                  0x0000000188320da8 ___CFRunLoopRun
6   CoreFoundation                  0x0000000188320354 _CFRunLoopRunSpecific
7   GraphicsServices                0x000000018a52079c _GSEventRunModal
8   UIKitCore                       0x00000001b47c9b68 _UIApplicationMain
9   Runner                          0x0000000106457c70 main main.m
10  libdyld.dylib                   0x0000000187de68e0 _start
```
#### 解决方案:
在engine(engine/src/flutter)中accessibility_bridge.mm添加bugfix代码。参见:
patches/stable_v1.0/engine#src#flutter/0006-Fix-accessibility-dealloc-resulted-crash.patch

功能优化
### Flutter拍摄视频等使用场景下的多余内存拷贝问题
#### 问题：
之前在视频拍摄的应用场景下，摄像头数据先会被拷贝到GPU中生成GPU纹理，然后基于纹理去实现美颜/滤镜等纹理操作，处理完成后如果需要给Flutter端显示预览数据，则需要将GPU数据拷贝到CPU中，再由Flutte Engine本身的纹理机制拷贝到GPU中生成纹理用于渲染。
修改后则将美颜/滤镜等纹理操作生成的纹理直接提供给Flutter Engine用于渲染。
#### 解决方案:
在engine(engine/src/flutter)中添加patch代码。参见:
patches/stable_v1.0/engine#src#flutter/0001-Add-external-surface-texture-support-By-luj.patch