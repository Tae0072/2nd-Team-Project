package com.qtai.bibleservice

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class BibleServiceApplication

fun main(args: Array<String>) {
    runApplication<BibleServiceApplication>(*args)
}