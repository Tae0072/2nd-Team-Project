package com.qtai.journalservice

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class JournalServiceApplication

fun main(args: Array<String>) {
    runApplication<JournalServiceApplication>(*args)
}