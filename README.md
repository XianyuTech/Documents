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

### iOS8 
#### 问题
系统语言设置成日文的情况下，部分汉字显示异常，成为小方格。
#### 错误现象(以flutter_gallery为例)
修复前:
![修复前](http://gw.alicdn.com/mt/TB1OixZoMHqK1RjSZFPXXcwapXa-640-1136.png)
修复后:
![修复后](http://gw.alicdn.com/mt/TB1K_d4oNTpK1RjSZFMXXbG_VXa-640-1136.png)

#### 问题分析:
iOS中的font查找是采用CTFontCreateForString函数，结合当前字体和文本在全局级联表(多态的, 基于用户语言设置和当前字体)下进行匹配，这在需要指定字体的场景下是不适用的。

因此可以采用kCTFontCascadeListAttribute指定所需的字体。

#### 解决方案:
在skia(engine/src/third_party/skia)中添加kCTFontCascadeListAttribute逻辑。参见:
patches/0001-Add-a-way-to-specify-fonts-in-flutter-iOS-avoid-the-.patch

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