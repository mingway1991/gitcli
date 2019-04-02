#!env/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import click
import yaml
from runshell import run_command
from file_helper import loadfile, writefile

reload(sys)
sys.setdefaultencoding('utf8')

'''
分支操作
gitcli switch-branch 'branch' 切换分支，并拉取最新提交
gitcli create-branch create 'branch' 创建新分支，同步到远端
gitcli delete-branch 'branch' 删除分支，同步到远端
gitcli clean-branches 只保留当前分支、master、release、develop

合并
gitcli merge 'branch' 合并某个分支，支持合并远端分支，(忽略合并某些文件或文件夹(从某个文件中读取配置)，某些冲突自动解决（从某个文件中读取配置）)

'''

class CatchAllExceptions(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as exc:
            click.secho('gitcli error: %s' % exc, fg='red')

@click.group(cls=CatchAllExceptions)
def gitcli():
    pass

@click.command(help='切换分支')
@click.option('-p', '--path', default=os.getcwd(), help='工作目录')
@click.option('-b', '--branch', help='分支名')
def switch_branch(path, branch):
    click.secho('切换分支')
    click.secho('工作目录: %s' % (path))
    if branch is None:
        raise Exception('缺少参数branch', fg='red')
    click.secho('分支名：%s' % (branch))
    errCode, stdMsg, errMsg = run_command('git checkout %s' % (branch), path)
    if errCode == 0:
        click.secho('切换分支成功', fg='green')
    else:
        click.secho('切换分支失败', fg='red')
        raise Exception(errMsg)
    errCode, stdMsg, errMsg = run_command('git pull', path)
    if errCode == 0:
        click.secho('拉取成功', fg='green')
    else:
        click.secho('拉取失败', fg='red')
        raise Exception(errMsg)

@click.command(help='创建新分支并推送到远端')
@click.option('-p', '--path', default=os.getcwd(), help='工作目录')
@click.option('-b', '--branch', help='分支名')
def create_branch(path, branch):
    click.secho('创建新分支')
    click.secho('工作目录: %s' % (path))
    if branch is None:
        raise Exception('缺少参数branch', fg='red')
    click.secho('分支名：%s' % (branch))
    errCode, stdMsg, errMsg = run_command('git branch %s' % (branch), path)
    if errCode == 0:
        click.secho('创建新分支成功', fg='green')
    else:
        click.secho('创建新分支失败', fg='red')
        raise Exception(errMsg)
    errCode, stdMsg, errMsg = run_command('git push -u origin %s' % (branch), path)
    if errCode == 0:
        click.secho('新分支推送远端成功', fg='green')
    else:
        click.secho('新分支推送远端失败', fg='red')
        raise Exception(errMsg)

@click.command(help='删除分支')
@click.option('-p', '--path', default=os.getcwd(), help='工作目录')
@click.option('-b', '--branch', help='分支名')
def delete_branch(path, branch):
    click.secho('删除分支')
    click.secho('工作目录: %s' % (path))
    if branch is None:
        raise Exception('缺少参数branch', fg='red')
    click.secho('分支名：%s' % (branch))
    errCode, stdMsg, errMsg = run_command('git branch -D %s' % (branch), path)
    if errCode == 0:
        click.secho('删除分支成功', fg='green')
    else:
        click.secho('删除分支失败', fg='red')
        raise Exception(errMsg)

@click.command(help='清理分支，保留当前分支\nmaster\nrelease\ndevelop')
@click.option('-p', '--path', default=os.getcwd(), help='工作目录')
def clean_branches(path):
    click.secho('清理分支')
    click.secho('工作目录: %s' % (path))
    errCode, stdMsg, errMsg = run_command('git branch', path)
    if errCode == 0:
        local_branches = stdMsg.split('\n')
        while '' in local_branches:
            local_branches.remove('')
        has_delete_branch = False
        for local_branch in local_branches:
            if local_branch.startswith('*'):
                continue
            local_branch_name = local_branch.replace(' ','')
            if local_branch_name != 'master' \
                and local_branch_name != 'release' \
                and local_branch_name != 'develop':
                errCode, stdMsg, errMsg = run_command('git branch -D %s' % (local_branch_name), path)
                if errCode == 0:
                    has_delete_branch = True
                    click.secho('删除分支%s成功' % (local_branch_name), fg='green')
                else:
                    click.secho('删除分支%s失败' % (local_branch_name), fg='red')
                    raise Exception(errMsg)
        if has_delete_branch is False:
            click.secho('没有需要删除的分支', fg='green')
        errCode, stdMsg, errMsg = run_command('git branch', path)
        if errCode == 0:
            click.secho('本地分支列表：')
            local_branches = stdMsg.split('\n')
            while '' in local_branches:
                local_branches.remove('')
            for local_branch in local_branches:
                click.secho(local_branch)
        else:
            click.secho('列出分支失败', fg='red')
            raise Exception(errMsg)
    else:
        click.secho('列出分支失败', fg='red')
        raise Exception(errMsg)

@click.command(help='合并分支')
@click.option('-p', '--path', default=os.getcwd(), help='工作目录')
@click.option('-b', '--branch', help='分支名')
def merge(path, branch):
    click.secho('合并分支')
    click.secho('工作目录: %s' % (path))
    if branch is None:
        raise Exception('缺少参数branch', fg='red')
    click.secho('分支名：%s' % (branch))
    #读取配置文件
    yml_path = os.path.join(path,'.gitcli.yml')
    merge_ignores = []
    conflict_resolve_by_self_files = []
    conflict_resolve_by_others_files = []
    content = loadfile(yml_path)
    if content is not None:
        temp = yaml.load(content, Loader=yaml.FullLoader)
        if temp.has_key('merge_ignores'):
            merge_ignores.extend(temp['merge_ignores'])
        if temp.has_key('conflict_resolve_by_self_files'):
            conflict_resolve_by_self_files.extend(temp['conflict_resolve_by_self_files'])
        if temp.has_key('conflict_resolve_by_others_files'):
            conflict_resolve_by_others_files.extend(temp['conflict_resolve_by_others_files'])
    click.secho('.gitcli.yml中配置的合并忽略文件：%s' % (merge_ignores))
    click.secho('.gitcli.yml中配置的冲突使用自己解决的文件：%s' % (conflict_resolve_by_self_files))
    click.secho('.gitcli.yml中配置的冲突使用对方解决的文件：%s' % (conflict_resolve_by_others_files))
    run_command('git merge %s --no-commit --no-ff' % (branch), path)
    for merge_ignore in merge_ignores:
        errCode, stdMsg, errMsg = run_command('git checkout HEAD -- %s && git reset HEAD %s' % (merge_ignore, merge_ignore), path)
        if errCode == 0:
            click.secho('合并忽略文件：%s' % (merge_ignore))
        else:
            click.secho('合并忽略文件：%s %s' % (merge_ignore, errMsg))
    errCode, stdMsg, errMsg = run_command('git clean -df', path)
    if errCode == 0:
        click.secho('清理不在版本库文件成功', fg='green')
    else:
        click.secho('清理不在版本库文件失败', fg='red')
    # 移除暂存区
    errCode, stdMsg, errMsg = run_command('git reset', path)
    if errCode != 0:
        raise Exception('移除暂存区出错:%s' % (errMsg))
    errCode, stdMsg, errMsg = run_command('GIT_PAGER='' git diff --name-only', path)
    modify_files = stdMsg.split('\n')
    while '' in modify_files:
        modify_files.remove('')
    if len(modify_files) == 0:
        click.secho('没有文件需要合并', fg='green')
        return
    #列出修改文件
    errCode, stdMsg, errMsg = run_command('GIT_PAGER='' git diff --name-only --diff-filter=U', path)
    conflict_files = stdMsg.split('\n')
    while '' in conflict_files:
        conflict_files.remove('')
    cannot_fix_conflict_files = []
    if len(conflict_files) != 0:
        #处理冲突
        click.secho('冲突文件列表:\n%s' % (stdMsg))
        for conflict_file in conflict_files:
            conflict_file_path = os.path.join(path,conflict_file)
            if conflict_file in conflict_resolve_by_self_files:
                #使用自己解决
                newcontent=''
                file_obj = open(conflict_file_path)
                all_lines = file_obj.readlines()
                in_conflict_head_block = False
                in_conflict_others_block = False
                for line in all_lines:
                    if line.startswith('<<<<<<<'):
                        in_conflict_head_block = True
                        continue
                    elif line.startswith('======='):
                        in_conflict_head_block = False
                        in_conflict_others_block = True
                        continue
                    elif line.startswith('>>>>>>>'):
                        in_conflict_others_block = False
                        continue
                    if in_conflict_head_block and not in_conflict_others_block:
                        newcontent += line
                    elif not in_conflict_head_block and in_conflict_others_block:
                        pass
                    else:
                        newcontent+=line
                writefile(conflict_file_path, newcontent)
            elif conflict_file in conflict_resolve_by_others_files:
                #使用对方解决
                newcontent = ''
                file_obj = open(conflict_file_path)
                all_lines = file_obj.readlines()
                in_conflict_head_block = False
                in_conflict_others_block = False
                for line in all_lines:
                    if line.startswith('<<<<<<<'):
                        in_conflict_head_block = True
                        continue
                    elif line.startswith('======='):
                        in_conflict_head_block = False
                        in_conflict_others_block = True
                        continue
                    elif line.startswith('>>>>>>>'):
                        in_conflict_others_block = False
                        continue
                    if in_conflict_head_block and not in_conflict_others_block:
                        pass
                    elif not in_conflict_head_block and in_conflict_others_block:
                        newcontent += line
                    else:
                        newcontent += line
                writefile(conflict_file_path, newcontent)
            else:
                cannot_fix_conflict_files.append(conflict_file)
        if len(cannot_fix_conflict_files) > 0:
            raise Exception('不能解决冲突文件列表:%s' % (cannot_fix_conflict_files))
    errCode, stdMsg, errMsg = run_command(
            'git add . && git commit -m \'gitcli: merge from %s\' && git push' % (branch), path)
    if errCode == 0:
        click.secho('合并提交成功', fg='green')
    else:
        click.secho('合并提交失败 %s' % (errMsg), fg='red')

gitcli.add_command(switch_branch)
gitcli.add_command(create_branch)
gitcli.add_command(delete_branch)
gitcli.add_command(clean_branches)
gitcli.add_command(merge)

if __name__ == '__main__':
    gitcli()