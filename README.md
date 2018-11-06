# 内容归档

## 构建相关
### Xcode10上如何自定义引擎构建

[ARMv7(iOS)-&-armeabi-v7a(Android)-build-with-Xcode10](https://github.com/flutter/engine/wiki/ARMv7(iOS)-&-armeabi-v7a(Android)-build-with-Xcode10)

### Android armeabi 构件支持

[armeabi-build-support](https://github.com/flutter/engine/wiki/Android-Builds-Supporting-armeabi)

## 工具链

## 文档

## C++支持

## 反射支持

## 包大小优化

## 性能调优

## 兼容性问题(中国市场)
### HUAWEI P6-T00 Android 4.2.2, API 17
####现象
Flutter页面黑并且Crash
####错误日志:
```
[ERROR:flutter/shell/platform/android/android_context_gl.cc(187)] Could not create an EGL context[ERROR:flutter/shell/platform/android/android_context_gl.cc(53)] EGL Error: EGL_BAD_MATCH (12297)
```
####解决方案:
错误时的容错逻辑(不会影响之前正常的设备)
参见patches/0001-A-workaround-for-devices-where-eglCreateContext-migh.patch

####问题跟踪::
https://github.com/flutter/engine/pull/6358




