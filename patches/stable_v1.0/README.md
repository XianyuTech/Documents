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

## 兼容性问题(中国市场)

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
patches/0001-A-workaround-for-devices-where-eglCreateContext-migh.patch

#### 问题跟踪::
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
patches/0001-Comment-out-GL_EXT_texture_buffer-related-logic-whic.patch

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
patches/0001-arm-intel-emulation-layer.patch

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
patches/0001-Remove-GL_EXT_debug_marker-related-logic-as-it-won-t.patch

### iOS上手势问题引起的flutter状态异常
#### 问题
Flutter页面点击事件在某些场景下失效
#### 错误现象
在某些场景下，如当Flutter页面与Native嵌套使用的时候，Flutter页面ListView中带小图可以点击查看大图(Push Native的ViewController展示)，大图上单击可以退出Native页面。这种场景下，连续两个手指点击会造成Flutter页面最后滑动异常，表现为页面卡顿或者点击事件不生效。

#### 问题分析
Flutter在iOS上的手势处理，数据来源于FlutterViewController的touchesBegan/touchesMoved/touchesEnded/touchesCancelled这四个函数。一个触摸事件的正常与结束，取决于开始(touchesBegan)同结束(touchesEnded/touchesCancelled)的对称关系。然而，在此种场景下，这种对称关系被破坏了。

#### 解决方案:
在engine(engine/src/flutter)中添加容错逻辑。参见:
patches/0001-Chinmay-6430-6145.patch

#### 问题跟踪
https://github.com/flutter/engine/pull/6145
