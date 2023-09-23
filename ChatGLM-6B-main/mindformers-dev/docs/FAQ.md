# FAQ 目录

[1.1 如何给MindSpore贡献代码](#11-如何给MindSpore贡献代码)

[1.2 多次提交记录，如何进行合并？](#12-多次提交记录如何进行合并)

[1.3 如何提交只有一个commit？](#13-如何提交只有一个commit)

[1.4 多人协作，如何解决代码上传冲突？](#14-多人协作如何解决代码上传冲突)

[1.5 开发过程中遇到问题，如果在开源社区中进行提问？](#15-开发过程中遇到问题如果在开源社区中进行提问)

[1.6 PR提交者是否需要签署CLA？](#16-pr提交者是否需要签署cla)

[1.7 PR提交时显示存在冲突，无法自动合并？](#17-pr提交时显示存在冲突无法自动合并)

[1.8 CI门禁检查提示的错误不在PR提交的内容中？](#18-ci门禁检查提示的错误不在pr提交的内容中)


# 1. FAQ 

在查看FAQ之前，请仔细阅读[代码提交注意指南](https://gitee.com/mindspore/vision/wikis/%E4%BB%A3%E7%A0%81%E6%8F%90%E4%BA%A4%E6%B3%A8%E6%84%8F%E6%8C%87%E5%8D%97)

## 1.1 如何给MindSpore贡献代码

请参考bilibili视频连接：[如何给MindSpore贡献代码](https://www.bilibili.com/video/BV1kg411F7Pc/)

![输入图片说明](https://images.gitee.com/uploads/images/2022/0414/171942_e6202765_7386274.png "屏幕截图.png")

视频会手把手带着大家如何贡献代码到gitee、如何fork MindSpore仓，并进行代码提交，解决git中username冲突等的问题。请一定要先观看该视频哦，会给您节省后续很多麻烦！



## 1.2 多次提交记录，如何进行合并

- 问题描述：
MindSpore transformer代码仓提交规范要求，提交记录仅保留一条，所以多次提交时，需要进行合并。

![输入图片说明](https://images.gitee.com/uploads/images/2022/0414/171522_cbcd9488_7386274.png "屏幕截图.png")

- 解决方案：

    1. 通过 git log 查看代码提交的log记录，使用 git rebase -i 选择要合并的 commit
    2. 编辑要合并的版本信息，即修改需要合并的 commit id 前面的pick修改为 squash，并保存提交
    3. 修改注释信息后，保存提交，多条合并会出现多次
    4. git push 推送远程仓库或合并到主干分支


## 1.3 如何提交只有一个commit

- 问题描述：

为了开源规范和方便审核，注意提交的时候只能有一个 commit：

![输入图片说明](https://images.gitee.com/uploads/images/2022/0414/170606_2dcf4944_7386274.png "屏幕截图.png")

- 解决方案：

    1. 修改代码之前，请先git fetch --all; git pull; 拉取最新的代码再修改
    2. 如果已经提交PR，此时可以基于上一个PR进行修改，使用 git add *; git commit --amend; git push -f;
    3. 通过commit --amend可以把当前的修改叠加到上一次代码中


## 1.4 多人协作，如何解决代码上传冲突

可能是已经有同学先合入代码了，再合入代码时，会报冲突。需要先把个人仓先更新一下。更新方法是：

`>>> git remote add upstream https://gitee.com/mindspore/vision.git`

这就把远端主仓添加到 upstream 里面了，然后使用命令 git merge：

`>>> git rebase upstream/master`


## 1.5 开发过程中遇到问题，如果在开源社区中进行提问？

在[transformer仓的issues区](https://gitee.com/mindspore/transformer/issues)提交issues，按照模板来描述问题，我们的工程师会在下面的comment留言哦。


## 1.6 PR提交者是否需要签署CLA？

PR的提交者，每一个都要根据提醒来签署CLA的，CLA是保障大家贡献的代码都能够得到开源保障，声明开发者是你本人哦。


## 1.7 PR提交时显示存在冲突，无法自动合并？

由于存在多人协作开发，因此在开发期间如果没有进行及时同步代码仓，则有可能出现冲突，在PR提交时无法自动合并。例如A团队的commit4与B团队的commit5存在冲突时，A团队的PR则无法提交。因此建议在PR提交前，同步最新的master分支，然后对开发分支进行rebase master操作。


## 1.8 CI门禁检查提示的错误不在PR提交的内容中？

无论是使用pycharm还是vscode等IDE进行开发，**请一定要安装autoPEP8等格式代码规范检查的工具**，每一次进行代码修改后，需要规范化代码，然后再进行提交。避免CI要等和阻塞等问题。

因部分静态检查工具引入或升级时，代码中已经存在一些拼写问题，而CI门禁中检查工具并不会对仓库中所有代码进行检查，所以可能会出现PR提交内容之外的错误。该问题涉及的是静态检查工具引入或升级后，该文件首次被修改，一般为一些简单的拼写错误，请按提示进行修正后重新触发门禁。

如果静态检查提示了一些错误，但是按照提示内容检查PR文件却未找到相关代码，请rebase最新代码后再按照提示进行修正。此问题出现的原因是三方开源检查工具小概率失效，导致错误放行并合入代码后，其它PR再次检查该处时报错。