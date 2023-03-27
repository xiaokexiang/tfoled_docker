## TFOLED Docker

### 前言
1. 基于[Nabaixin/TFOLED](https://github.com/Nabaixin/TFOLED)的基础上进行封装的docker版本。
2. 入手树莓派4B以来每次都要重新安装一次，tfoled依赖python，还受到内核版本的影响，之前使用`raspberrypi os`时安装会出现依赖问题，折腾了好长时间，最后使用`aptitude`才成功安装。
3. 因为喜欢不停的换系统，从raspberrypi os、ubuntu lts到现在基于openwrt的`iStoreOS`， 在这个上面太费时间，所以就制作了一个docker版的tfoled来提高效率。

### 前置准备
在raspberrypi os或者ubuntu中可以通过`raspi-config`开启I2C功能，但是在基于`openwrt`的`iStoreOS`中需要安装一些依赖包才可以实现I2C功能。
```bash
# 安装依赖包
opkg update
opkg install i2c-tools kmod-i2c-gpio kmod-i2c-algo-bit kmod-i2c-algo-pcf kmod-i2c-bcm2835 kmod-i2c-core kmod-i2c-gpio kmod-i2c-mux python3-smbus
# 修改配置
echo "dtparam=i2c_arm=on
dtparam=i2c0=on
dtparam=i2c1=on
dtparam=spi=on
dtparam=i2s=on" >> /boot/config.txt
# 重启即可
```

### 部署
```bash
docker run -itd --name tfoled \
   --privileged \
   --net=host \
   -e upper=40  \ # 风扇启动的温度，不填默认45
   -e lower=38 \ # 风扇停止的温度，不填默认42
   -d xiaokexiang/ubuntu-tfoled
```
