###################################################################
#           Copyright (c) 2016 by TAOS Technologies, Inc.
#                     All rights reserved.
#
#  This file is proprietary and confidential to TAOS Technologies.
#  No part of this file may be reproduced, stored, transmitted,
#  disclosed or used in any form or by any means other than as
#  expressly provided by the written permission from Jianhui Tao
#
###################################################################

# -*- coding: utf-8 -*-
from util.log import tdLog
from util.cases import tdCases
from util.sql import tdSql
import time 
from util.common import tdCom


class TDTestCase:
    def init(self, conn, logSql):
        tdLog.debug("start to execute %s" % __file__)
        tdSql.init(conn.cursor(), logSql)

    def checkMemDiskMerge(self):
        tb_name = tdCom.getLongName(8, "letters")
        tdSql.execute(
            f'CREATE TABLE {tb_name} (ts timestamp, c1 int, c2 int)')
        tdSql.execute(
            f'insert into {tb_name} values ("2021-01-01 12:00:00.000", 1, 1)')
        tdSql.execute(
            f'insert into {tb_name} values ("2021-01-03 12:00:00.000", 3, 3)')
        tdCom.restartTaosd()
        tdSql.execute(
            f'insert into {tb_name} values ("2021-01-02 12:00:00.000", Null, 2)')
        tdSql.execute(
            f'insert into {tb_name} values ("2021-01-04 12:00:00.000", Null, 4)')
        query_sql = f'select * from {tb_name}'
        res1 = tdSql.query(query_sql, True)
        tdCom.restartTaosd()
        res2 = tdSql.query(query_sql, True)
        for i in range(4):
            tdSql.checkEqual(res1[i], res2[i])
    
    def checkSuperSubBlockMerge(self):
        tdCom.cleanTb()
        tb_name = tdCom.getLongName(8, "letters")
        tdSql.execute(
            f'CREATE TABLE {tb_name} (ts timestamp, c1 int)')

        start_ts = 1577808001000
        for i in range(80):
            tdSql.execute(
                f'insert into {tb_name} values ({start_ts}, {i})')
            start_ts += 1
        tdCom.restartTaosd()

        tdSql.query(f'select * from {tb_name}')
        for i in range(10):
            tdSql.execute(
                f'insert into {tb_name} values ({start_ts}, Null)')
            start_ts += 1
        tdCom.restartTaosd()

        tdSql.query(f'select * from {tb_name}')
        for i in range(10):
            new_ts = i + 10 + 10
            tdSql.execute(
                f'insert into {tb_name} values ({start_ts}, {new_ts})')
            start_ts += 1
        tdCom.restartTaosd()
        tdSql.query(f'select * from {tb_name}')

    def run(self):
        tdSql.prepare()
        # self.checkMemDiskMerge()
        self.checkSuperSubBlockMerge()

    def stop(self):
        tdSql.close()
        tdLog.success("%s successfully executed" % __file__)


tdCases.addWindows(__file__, TDTestCase())
tdCases.addLinux(__file__, TDTestCase())
