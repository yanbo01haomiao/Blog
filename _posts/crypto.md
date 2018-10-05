# 对称/非对称加密技术与哈希算法

本文通过对具体的AES、RSA这两种具体的加密算法以及MD5哈希算法来讲解关于对称/非对称加密技术和消息摘要技术。以对这方面的知识形成初步认识以及明白他们之间的分别.

## 对称密钥加密算法AES

AES是一种较为常见的对称加密算法,加密和解密使用相同的密钥,具体的加解密流程如下图

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/crypto/aes.png)

- 加密(Encrypt)的过程可以抽象为C = E(K,P) 即把密钥K和明文P作为参数传入加密函数E,输出密文C
- 解密(Decrypt)的过程可以抽象为P = D(K,C) 即把密钥K和密文C作为参数传入解密函数D,输出明文P

加解密算法具体是怎么实现比较复杂,我也没有去了解.但是可知的是加解密算法没有损耗信息的完整性.我们可以从加密后的密文解密出原文.

*课程作业老师要求用java,所以重拾了一下java..*

```java
// 使用了BouncyCastle提供的jar包做了一个AES加解密Demo
import org.bouncycastle.jce.provider.BouncyCastleProvider;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.security.Security;

public class AES {

    private static byte[] iv = { 0x38, 0x37, 0x36, 0x35, 0x34, 0x33, 0x32, 0x31, 0x38, 0x37,
            0x36, 0x35, 0x34, 0x33, 0x32, 0x31 };
    static {
        Security.addProvider(new BouncyCastleProvider()); //会在类被加载的时候执行且仅会被执行一次
    }

    public static byte[] encrypt(byte[] plaintext, String skey) throws Exception {
        Key key = new SecretKeySpec(skey.getBytes("utf-8"), "AES"); // 密钥K
        Cipher in = Cipher.getInstance("AES/CBC/PKCS7Padding", "BC"); //"算法/模式/补码方式"
        in.init(Cipher.ENCRYPT_MODE, key, new IvParameterSpec(iv));//使用CBC模式，需要一个向量iv，可增加加密算法的强度
        byte[] ciphertext = in.doFinal(plaintext);
        return ciphertext;
    }
    public static byte[] decrypt(byte[] cipher, String skey) throws Exception {
        Key key = new SecretKeySpec(skey.getBytes("utf-8"), "AES");
        Cipher out = Cipher.getInstance("AES/CBC/PKCS7Padding","BC");
        out.init(Cipher.DECRYPT_MODE,key,new IvParameterSpec(iv));
        byte[] decrypttext = out.doFinal(cipher);
        return decrypttext;
    }
    public static void main(String[] args) throws Exception{
        String key = "11147169444463676897639210105259";
        byte[] ciphertext = encrypt("蔡晓聪".getBytes("utf-8"),key);
        System.out.println("密文:" + new String(ciphertext,"utf-8"));
        byte[] decrypttext = decrypt(ciphertext,key);
        System.out.println("解密后原文:" + new String(decrypttext,"utf-8"));
    }
}
```

> 这个demo实现的时候遇到一个坑,美国政府对JCE(Java Cryptography Extension)的出口做了限制,所以在使用上面的AES128位加密的时候报了一个错误,网上查询之后,到oracle官网下载一个Unlimited的[jce_policy(jdk1.8版本)](https://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html)替换本地jdk的相同文件即可解决

*后面发现题目看错了,老师要求的是DES,所以又写了DES版本,可以看到同为对称加密算法,DES的外部表现和AES很像*

```java
// DES一次一密的加解密Demo
import org.bouncycastle.crypto.BlockCipher;
import org.bouncycastle.crypto.BufferedBlockCipher;
import org.bouncycastle.crypto.engines.DESEngine;
import org.bouncycastle.crypto.modes.CBCBlockCipher;
import org.bouncycastle.crypto.paddings.PaddedBufferedBlockCipher;
import org.bouncycastle.crypto.params.KeyParameter;

public class DES {

    static BlockCipher engine = new DESEngine();

    public static byte[] encrypt(byte[] plainText, String keys) throws Exception{
        byte[] key = keys.getBytes();
        byte[] ptBytes = plainText;
        BufferedBlockCipher cipher = new PaddedBufferedBlockCipher(new CBCBlockCipher(engine));
        cipher.init(true, new KeyParameter(key));
        byte[] rv = new byte[cipher.getOutputSize(ptBytes.length)];
        int tam = cipher.processBytes(ptBytes, 0, ptBytes.length, rv, 0);
        cipher.doFinal(rv, tam);
        return rv;
    }
    public static byte[] decrypt(byte[] cipherText, String keys) throws Exception{
        byte[] key = keys.getBytes();
        BufferedBlockCipher cipher = new PaddedBufferedBlockCipher(new CBCBlockCipher(engine));
        cipher.init(false, new KeyParameter(key));
        byte[] rv = new byte[cipher.getOutputSize(cipherText.length)];
        int tam = cipher.processBytes(cipherText, 0, cipherText.length, rv, 0);
        cipher.doFinal(rv, tam);
        return rv;
    }
    public static void main(String[] args) throws Exception{
        String key = "" + (int)((Math.random()*9+1)*10000000); // 一次一密，每次生成不同的8位密钥，可以看到不同密钥加密后的密文不同
        System.out.println("Key:" + key);
        byte[] ciphertext = encrypt("蔡晓聪".getBytes("utf-8"),key);
        System.out.println("密文:" + new String(ciphertext,"utf-8"));
        byte[] decrypttext = decrypt(ciphertext,key);
        System.out.println("解密后原文:" + new String(decrypttext,"utf-8"));
    }
}
```

## 非对称加密算法RSA

*RSA这个单词不是什么英文缩写,而是算法的创始人三人中姓氏的开头字母拼接的*

RSA加密算法是一种非对称加密算法,在公开密钥加密领域中被广泛使用.我相信使用过SSH来登录GitHub的用户对此会略有印象.我自己最初也是为GitHub关联SSH keys的时候才开始接触.

简单讲一下关于非对称加密算法的原理和作用.考虑如下这样的场景:

Alice和Bob想通过一个不可靠的媒介(例如HTTP就是一个不可靠的媒介)传输一条私密消息,这时候为了保证消息不暴露和不被第三方窃取,此时考虑使用非对称加密算法来完成这个需求.

1. Alice通过一系列的[公钥与私钥的产生方法](https://zh.wikipedia.org/wiki/RSA%E5%8A%A0%E5%AF%86%E6%BC%94%E7%AE%97%E6%B3%95#%E5%85%AC%E9%92%A5%E4%B8%8E%E7%A7%81%E9%92%A5%E7%9A%84%E4%BA%A7%E7%94%9F)生成一对密钥,分别为公钥和私钥.

2. Alice将公钥发送给Bob,同时公钥可以随意公开.第三方攻击者也可以拥有这个公钥

3. Bob想给Alice发送一条私密消息,Bob使用Alice给他的 **公钥**来 **加密**这条消息,将加密完的密文发送给Alice.
*此时密文被他人窃取也完全没问题,攻击者用公钥无法解密出原文,只看密文无法获知该私密消息*

4. Alice收到密文之后,通过自己的私钥(与给Bob的公钥配对的私钥)解密接收到的密文,得到Bob发送给自己的原文.

*如果Alice想给Bob写回信,那么就需要Bob也像Alice一样生成一对密钥,并把公钥发给Alice,然后执行和Alice上述所作的所有步骤*

```java
// RSA公钥加密私钥解密小demo
import org.bouncycastle.crypto.AsymmetricBlockCipher;
import org.bouncycastle.crypto.AsymmetricCipherKeyPair;
import org.bouncycastle.crypto.CipherParameters;
import org.bouncycastle.crypto.InvalidCipherTextException;
import org.bouncycastle.crypto.engines.RSAEngine;
import org.bouncycastle.crypto.params.RSAKeyGenerationParameters;
import org.bouncycastle.crypto.generators.RSAKeyPairGenerator;
import org.bouncycastle.jce.provider.BouncyCastleProvider;

import java.io.*;
import java.math.BigInteger;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.Security;

public class RSA {

    // 生成密钥对的方法
    public static AsymmetricCipherKeyPair GenerateKeys() throws NoSuchAlgorithmException {
        RSAKeyPairGenerator generator = new RSAKeyPairGenerator();
        generator.init(new RSAKeyGenerationParameters
           (
                new BigInteger("10001", 16),
                SecureRandom.getInstance("SHA1PRNG"),
                4096,
                80
           ));

        return generator.generateKeyPair();
    }

    public static byte[] Encrypt(byte[] data, CipherParameters publicKey) throws Exception {
        Security.addProvider(new BouncyCastleProvider());

        RSAEngine engine = new RSAEngine();
        engine.init(true,publicKey);

        byte[] hexEncodedCipher = engine.processBlock(data, 0, data.length);
        return hexEncodedCipher;
    }

    public static byte[] Decrypt(byte[] encrytedData, CipherParameters privateKey) throws InvalidCipherTextException {
        Security.addProvider(new BouncyCastleProvider());

        AsymmetricBlockCipher engine = new RSAEngine();
        engine.init(false, privateKey);

        byte[] hexEncodedCipher = engine.processBlock(encrytedData,0,encrytedData.length);

        return hexEncodedCipher;
    }

    public static void main(String[] args) throws Exception {
        AsymmetricCipherKeyPair keyPair = GenerateKeys(); // 生成密钥对
        File file = new File("test-1.txt");
        FileInputStream in = new FileInputStream(file);
        ByteArrayOutputStream bout = new ByteArrayOutputStream();
        byte[] tmpbuf = new byte[1024];
        int count = 0;
        while ((count = in.read(tmpbuf)) != -1){
            bout.write(tmpbuf,0,count);
            tmpbuf = new byte[1024];
        }
        in.close();
        byte[] orgData = bout.toByteArray();// orgData得到test-1.txt的二进制数据
        byte[] encryptData = Encrypt(orgData, keyPair.getPublic()); // 公钥加密
        file = new File("encrypt_result.txt");
        OutputStream out = new FileOutputStream(file);
        out.write(encryptData);
        System.out.println("公钥加密成功!结果存于: " + file.getAbsolutePath()); // 输出文件的位置
        out.close();
        byte[] decryptData = Decrypt(encryptData, keyPair.getPrivate()); // 私钥解密
        file = new File("decrypt_result.txt");
        out = new FileOutputStream(file);
        out.write(decryptData);
        System.out.println("私钥解密成功!结果存于: " + file.getAbsolutePath()); // 输出文件的位置
        out.flush();
        out.close();
    }
}
```
**我觉得RSA最精彩的实践在https传输中用于加密[对称加密算法密钥]的时候,可以参考下面另一篇关于https的博文**
- 参考资料
[bouncycastle的jar包实现RSA](https://github.com/anonrig/bouncycastle-implementations/blob/master/rsa.java)
[今夜我们一起学习HTTP之https](https://github.com/caistrong/Blog/issues/48)

## 哈希算法MD5

简单概括,MD5算法（英语：MD5 Message-Digest Algorithm）就是MD5是输入不定长度信息，输出固定长度128-bits的算法。通俗的讲,就是根据输入内容生成一个该内容对应的固定长度的摘要信息.当内容有略微不同的时候,输出的摘要信息将大不相同.

从输出固定长度这点可以看出,哈希算法不像上面的两种加密算法,哈希算法会导致信息缺失,无法像加密算法有解密这样逆向的过程,而是不可逆的.哈希算法与对称/非对称加密算法有根本上的不同,其在信息安全领域有其不同的用武之处.

例如,服务器提供一个文件的下载,服务器先使用md5算法生成该文件的摘要信息.当用户下载该文件到本地后.再同样使用md5算法自己生成一遍摘要看看和服务器生成的摘要信息是否相同.当下载线路上有中间人恶意篡改了文件的内容将会导致生成的摘要信息变更,这样用户就可以知道

再比如,在开发服务器APP时,对于一些敏感信息,例如用户账户密码和用户手机号等,一般不会明文存储在数据库,因为如果明文存储的话,当数据库被拖库时用户的个人信息将全部沦陷.因此我们一般对用户的敏感信息经过像md5这样的哈希算法生成其摘要存入数据库.而不直接存明文.当用户输入明文密码登录时,我们将该密码再次hash生成摘要,对比存于数据库中的摘要,若二者相同时代表用户密码输入正确.

*一般而言,不同的内容只有极小的概率生成相同的摘要*

```java
//bouncycastle的md5工具demo代码
import org.bouncycastle.crypto.digests.MD5Digest;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.util.encoders.Hex;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.security.Security;

public class MD5 {
    public static void main(String[] args) throws Exception{
        Security.addProvider(new BouncyCastleProvider());

        File file = new File("test-1.txt");
        FileInputStream in = new FileInputStream(file);
        ByteArrayOutputStream bout = new ByteArrayOutputStream();
        byte[] tmpbuf = new byte[1024];
        int count = 0;
        while ((count = in.read(tmpbuf)) != -1){
            bout.write(tmpbuf,0,count);
            tmpbuf = new byte[1024];
        }
        in.close();

        byte[] input = bout.toByteArray();
        MD5Digest md5 = new MD5Digest();
        md5.update(input, 0 , input.length);
        byte[] digest = new byte[md5.getDigestSize()];
        md5.doFinal(digest,0);

        System.out.println("输入："+ new String(input));
        System.out.println("输入(Hex)："+ new String(Hex.encode(input)));
        System.out.println("输出(Hex)："+ new String(Hex.encode(digest)));

    }
}

```

- 参考资料
[Java Bouncycastle MD5](https://myprogramminglab.blogspot.com/2010/01/java-bouncycastle-md5-example.html)