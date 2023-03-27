## TFOLED Docker

### 前言
1. 基于[Nabaixin/TFOLED](https://github.com/Nabaixin/TFOLED)的基础上进行封装的docker版本。
2. 入手树莓派4B以来每次都要重新安装一次，tfoled依赖python，还受到内核版本的影响，之前使用`raspberrypi os`时安装会出现依赖问题，折腾了好长时间，最后使用`aptitude`才成功安装。
3. 因为喜欢不停的换系统，从raspberrypi os、ubuntu lts到现在基于openwrt的`iStoreOS`， 在这个上面太费时间，所以就制作了一个docker版的tfoled来提高效率。

### 部署
```bash
docker run -itd --name tfoled \
   --privileged \
   --net=host \
   -e upper=40  \ # 风扇启动的温度，不填默认45
   -e lower=38 \ # 风扇停止的温度，不填默认42
   -d xiaokexiang/ubuntu-tfoled
```
